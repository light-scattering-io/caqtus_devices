"""
This package defines a RuntimeDevice class that is used to control Thorlabs Elliptec
ELL14 rotation stages.
"""

import contextlib
import time
from typing import Optional

from attrs import define, field
from attrs.setters import frozen
from attrs.validators import instance_of, optional
from caqtus.device import RuntimeDevice
from caqtus.types.recoverable_exceptions import ConnectionFailedError
from serial import SerialException
from thorlabs_elliptec import ELLx, ELLStatus


@define
class ElliptecELL14RotationStage(RuntimeDevice):
    """A class for controlling Thorlabs Elliptec ELL14 rotation stages.

    Attributes:
        serial_port: The serial port to use to communicate with the device. e.g. "COM9"
        device_id: The device ID of the device.
        This is what is referred as the address in the thorlabs Ello software.
        If the device is used in multi-port mode, a single serial port can control
        multiple devices with different device IDs.
        However, this is not supported at the moment and only one device can be
        instantiated for a given serial port.
    """

    serial_port: str = field(validator=instance_of(str), on_setattr=frozen)
    device_id: int = field(validator=instance_of(int), on_setattr=frozen)
    initial_position: Optional[float] = field(
        default=None, validator=optional(instance_of(float)), on_setattr=False
    )

    _device: ELLx = field(init=False)

    def initialize(self) -> None:
        """Connect to the device and initialize it."""

        super().initialize()

        for attempt in range(3):
            try:
                self._device = self._enter_context(
                    contextlib.closing(
                        ELLx(
                            serial_port=self.serial_port, x=14, device_id=self.device_id
                        )
                    )
                )
                break
            except SerialException:
                pass
        else:
            raise ConnectionFailedError(
                f"Could not open serial port {self.serial_port}"
            )
        while self._device.status != ELLStatus.OK:
            time.sleep(0.1)

        if self.initial_position is not None:
            self._update_position(self.initial_position)

    def update_parameters(self, position: float) -> None:
        """Move the stage to the given position.

        Args:
            position: The position to move the stage to in degrees.
        """

        # We don't want to move the stage if it is already at the desired position.
        # This is because the stage takes some tens of milliseconds to move even if it
        # is already at the right place.
        # Plus, the stage might overheat if it is unnecessarily moved too often.
        # To prevent this, we only move the stage if it is far from the desired
        # position.

        previous_position = self.read_position()

        tolerance = 0.01  # degrees
        if abs(position - previous_position) > tolerance:
            self._update_position(position)

    def _update_position(self, position: float):
        try:
            self._device.move_absolute(position, blocking=True)
        except Exception as error:
            raise RuntimeError(
                f"Could not move device {self.name} to position {position}"
            ) from error

    def read_position(self) -> float:
        """The current position of the stage in degrees."""

        if self._device is None:
            raise RuntimeError(f"Device {self.name} was not started")
        return self._device.get_position()
