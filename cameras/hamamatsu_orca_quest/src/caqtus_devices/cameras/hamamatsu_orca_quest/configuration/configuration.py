from __future__ import annotations

import enum
from typing import TYPE_CHECKING

import attrs
from caqtus.device.camera import CameraConfiguration
from caqtus.types.image import Width, Height
from caqtus.types.image.roi import RectangularROI
from caqtus.utils import serialization

if TYPE_CHECKING:
    # We avoid importing the runtime module because it imports the dcam dependency that
    # might not be installed in the current environment.
    from ..runtime import OrcaQuestCamera # noqa: F401


class SensorMode(enum.Enum):
    AREA = "Area"
    PHOTON_NUMBER_RESOLVING = "Photon number resolving"

    def __str__(self):
        return self.value

class ReadoutSpeed(enum.Enum):
    SLOWEST = "Slowest"
    FASTEST = "Fastest"

    def __str__(self):
        return self.value


@attrs.define
class OrcaQuestCameraConfiguration(CameraConfiguration["OrcaQuestCamera"]):
    """Holds the configuration for an OrcaQuest camera.

    Attributes:
        camera_number: The number of the camera to use.
        sensor_mode: Whether to use the camera in area or photon number resolving mode.
        readout_speed: The readout speed of the camera.
            When the sensor mode is set to photon number resolving, only slowest
            readout speed is possible.
    """

    camera_number: int = attrs.field(converter=int, on_setattr=attrs.setters.convert)
    sensor_mode: SensorMode = attrs.field(default=SensorMode.AREA)
    readout_speed: ReadoutSpeed = attrs.field(default=ReadoutSpeed.FASTEST)

    @classmethod
    def dump(cls, config: OrcaQuestCameraConfiguration) -> serialization.JSON:
        return serialization.unstructure(config)

    @classmethod
    def load(cls, data: serialization.JSON) -> OrcaQuestCameraConfiguration:
        return serialization.structure(data, OrcaQuestCameraConfiguration)

    @classmethod
    def default(cls) -> OrcaQuestCameraConfiguration:
        return OrcaQuestCameraConfiguration(
            camera_number=0,
            remote_server=None,
            roi=RectangularROI(
                original_image_size=(Width(4096), Height(2304)),
                x=0,
                y=0,
                width=4096,
                height=2304,
            ),
        )
