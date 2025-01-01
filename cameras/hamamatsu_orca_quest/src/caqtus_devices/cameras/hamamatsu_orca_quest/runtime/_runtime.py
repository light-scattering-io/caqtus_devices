import contextlib
import time
from typing import Any, ClassVar, Optional, Self

from attrs import define, field
from attrs.setters import frozen
from attrs.validators import instance_of

from caqtus.device.camera import Camera, CameraTimeoutError
from caqtus.types.recoverable_exceptions import ConnectionFailedError
from caqtus.utils import log_exception
from caqtus.utils.context_managers import close_on_error
from . import dcam, dcamapi4
from ._logger import logger

BUFFER_SIZE = 10


@define(slots=False)
class OrcaQuestCamera(Camera):
    """

    Beware that not all roi values are allowed for this camera.
    In doubt, try to check if the ROI is valid using the HCImageLive software.

    Attributes:
        camera_number: The camera number used to identify the specific camera.
    """

    sensor_width: ClassVar[int] = 4096
    sensor_height: ClassVar[int] = 2304

    camera_number: int = field(validator=instance_of(int), on_setattr=frozen)

    _camera: "dcam.Dcam" = field(init=False)
    _buffer_number_pictures: Optional[int] = field(init=False, default=None)
    _exit_stack: contextlib.ExitStack = field(init=False, factory=contextlib.ExitStack)

    def _read_last_error(self) -> str:
        return dcam.DCAMERR(self._camera.lasterr()).name

    def update_parameters(self, timeout: float) -> None:
        self.timeout = timeout

    def __enter__(self) -> Self:
        with close_on_error(self._exit_stack):
            self._initialize()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self._exit_stack.__exit__(exc_type, exc_value, traceback)

    @log_exception(logger)
    def _initialize(self) -> None:
        if dcam.Dcamapi.init():
            self._exit_stack.callback(dcam.Dcamapi.uninit)
        else:
            # If this error occurs, check that the dcam-api from hamamatsu is installed
            # https://dcam-api.com/
            raise ImportError(
                f"Failed to initialize DCAM-API: {dcam.Dcamapi.lasterr().name}"
            )

        if self.camera_number < dcam.Dcamapi.get_devicecount():
            self._camera = dcam.Dcam(self.camera_number)
        else:
            raise ConnectionFailedError(f"Could not find camera {self.camera_number}")

        if not self._camera.dev_open():
            raise ConnectionFailedError(
                f"Failed to open camera {self.camera_number}: {self._read_last_error()}"
            )
        self._exit_stack.callback(self._camera.dev_close)

        if not self._camera.prop_setvalue(
            dcamapi4.DCAM_IDPROP.SUBARRAYMODE, dcamapi4.DCAMPROP.MODE.OFF
        ):
            raise RuntimeError(
                f"can't set subarray mode off: {self._read_last_error()}"
            )

        properties = {
            dcamapi4.DCAM_IDPROP.SUBARRAYHPOS: self.roi.x,
            dcamapi4.DCAM_IDPROP.SUBARRAYHSIZE: self.roi.width,
            dcamapi4.DCAM_IDPROP.SUBARRAYVPOS: self.roi.y,
            dcamapi4.DCAM_IDPROP.SUBARRAYVSIZE: self.roi.height,
            dcamapi4.DCAM_IDPROP.SENSORMODE: dcamapi4.DCAMPROP.SENSORMODE.AREA,
            dcamapi4.DCAM_IDPROP.TRIGGER_GLOBALEXPOSURE: dcamapi4.DCAMPROP.TRIGGER_GLOBALEXPOSURE.DELAYED,
        }

        if self.external_trigger:
            # The Camera is set to acquire images when the trigger is high.
            # This allows changing the exposure by changing the trigger duration and
            # without having to communicate with the camera.
            # With this it is possible to change the exposure of two very close
            # pictures.
            # However, the trigger received by the camera must be clean.
            # If it bounces, the acquisition will be messed up.
            # To prevent bouncing, it might be necessary to add a 50 Ohm resistor
            # before the camera trigger input.
            properties[dcamapi4.DCAM_IDPROP.TRIGGERSOURCE] = (
                dcamapi4.DCAMPROP.TRIGGERSOURCE.EXTERNAL
            )
            properties[dcamapi4.DCAM_IDPROP.TRIGGERACTIVE] = (
                dcamapi4.DCAMPROP.TRIGGERACTIVE.LEVEL
            )
            properties[dcamapi4.DCAM_IDPROP.TRIGGERPOLARITY] = (
                dcamapi4.DCAMPROP.TRIGGERPOLARITY.POSITIVE
            )
        else:
            raise NotImplementedError("Only external trigger is supported")
            # Need to handle different exposures when using internal trigger, so it is
            # not implemented yet.
            # properties[DCAM_IDPROP.TRIGGERSOURCE] = DCAMPROP.TRIGGERSOURCE.INTERNAL

        for property_id, property_value in properties.items():
            if not self._camera.prop_setvalue(property_id, property_value):
                raise RuntimeError(
                    f"Failed to set property {property_id} to {property_value}:"
                    f" {self._read_last_error()}"
                )

        if not self._camera.prop_setvalue(
            dcamapi4.DCAM_IDPROP.SUBARRAYMODE, dcamapi4.DCAMPROP.MODE.ON
        ):
            raise RuntimeError(f"can't set subarray mode on: {self._read_last_error()}")

        if not self._camera.buf_alloc(BUFFER_SIZE):
            raise RuntimeError(
                f"Failed to allocate buffer for images: {self._read_last_error()}"
            )
        self._exit_stack.callback(self._camera.buf_release)

        for property_name, value in self.list_properties().items():
            logger.debug("Property %s: %f", property_name, value)

    @contextlib.contextmanager
    def acquire(self, exposures: list[float]):
        if len(exposures) > BUFFER_SIZE:
            raise ValueError(
                f"Can't acquire {len(exposures)} images, the maximum number of images"
                f" that can be acquired is {BUFFER_SIZE}"
            )
        self._start_acquisition()
        try:
            yield self._read_images(exposures)
        finally:
            self._stop_acquisition()

    def _start_acquisition(self) -> None:
        if not self._camera.cap_start(bSequence=True):
            raise RuntimeError(f"Can't start acquisition: {self._read_last_error()}")

    def _stop_acquisition(self) -> None:
        if not self._camera.cap_stop():
            raise RuntimeError(f"Failed to stop acquisition: {self._read_last_error()}")

    def _read_images(self, exposures: list[float]):
        # Should change the exposure time if using internal trigger, but don't need to
        # do it now as we only support external trigger.
        # self._camera.prop_setvalue(DCAM_IDPROP.EXPOSURETIME, new_exposure)

        acquisition_start_time = time.monotonic()
        next_frame = 0

        while next_frame < len(exposures):
            # wait_capevent_frameready will only wait 50 ms if not acquisition occurred
            # in that time.
            # If a picture is available before, it will return at that moment, so it
            # should be reactive.
            if self._camera.wait_capevent_frameready(50):
                # More than one picture might have been acquired since the last
                # wait_capevent_frameready, so we need to handle possibly multiple
                # pictures.
                transfer_info = self._camera.cap_transferinfo()
                if not transfer_info:
                    raise RuntimeError(
                        f"Failed to get capture transfer info: {self._camera.lasterr()}"
                    )
                for frame in range(
                    next_frame, int(transfer_info.nNewestFrameIndex) + 1
                ):
                    logger.debug("Reading frame %d", frame)
                    image = self._camera.buf_getframedata(frame)
                    if image is not None:
                        yield image.T
                    else:
                        raise RuntimeError(
                            f"Failed to get image data: {self._camera.lasterr()}"
                        )
                next_frame = int(transfer_info.nNewestFrameIndex) + 1
            else:
                error = self._camera.lasterr()
                if error.is_timeout():
                    # elapsed refer to beginning of acquisition, so the timeout is for
                    # all the pictures and not between two pictures.
                    elapsed = time.monotonic() - acquisition_start_time
                    if elapsed < self.timeout:
                        continue
                    else:
                        raise CameraTimeoutError(
                            f"Timed out after {self.timeout * 1e3:.0f} ms without "
                            f"receiving a trigger"
                        )
                else:
                    raise RuntimeError(f"An error occurred during acquisition: {error}")

    def list_properties(self) -> dict[str, float]:
        result = {}
        property_id = self._camera.prop_getnextid(0)
        while property_id:
            property_name = self._camera.prop_getname(property_id)
            if property_name:
                value = self._camera.prop_getvalue(property_id)
                if value is not False:
                    result[property_name] = value
                else:
                    raise RuntimeError(
                        f"Failed to get property value for {property_name}:"
                        f" {self._camera.lasterr()}"
                    )
            else:
                raise RuntimeError(
                    f"Failed to get property name for {property_id}:"
                    f" {self._camera.lasterr()}"
                )
            property_id = self._camera.prop_getnextid(property_id)
            if property_id is False:
                raise RuntimeError(
                    f"Failed to get next property id after {property_id}:"
                    f" {self._camera.lasterr()}"
                )
        return result

    @classmethod
    def list_camera_infos(cls) -> list[dict[str, Any]]:
        result = []
        for camera_index in range(dcam.Dcamapi.get_devicecount()):
            infos = {}
            camera = dcam.Dcam(camera_index)
            infos["id"] = camera.dev_getstring(dcamapi4.DCAM_IDSTR.CAMERAID)
            infos["model"] = camera.dev_getstring(dcamapi4.DCAM_IDSTR.MODEL)
            infos["camera version"] = camera.dev_getstring(
                dcamapi4.DCAM_IDSTR.CAMERAVERSION
            )
            infos["driver version"] = camera.dev_getstring(
                dcamapi4.DCAM_IDSTR.DRIVERVERSION
            )
            result.append(infos)
        return result
