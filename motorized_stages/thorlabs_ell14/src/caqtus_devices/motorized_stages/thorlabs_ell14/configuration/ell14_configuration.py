import logging
from typing import Any, Self, TYPE_CHECKING

import attrs
from caqtus.device import DeviceConfiguration
from caqtus.types.expression import Expression
from caqtus.utils import serialization

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ..runtime import ElliptecELL14RotationStage

logger = logging.getLogger(__name__)


@attrs.define
class ElliptecELL14RotationStageConfiguration(
    DeviceConfiguration["ElliptecELL14RotationStage"]
):
    """Holds static configuration to control an ELL14 rotation stage device

    Attributes:
        serial_port: The serial port to use to communicate with the device.

            For example, "COM9"

        device_id: The ID of the device.

            This is what is referred as the address in the thorlabs Ello software. If
            the device is used in multi-port mode, a single serial port can control
            multiple devices with different device IDs. However, this is not supported
            at the moment and only one device can be instantiated for a given serial
            port.

        position: The position of the stage.

            This can be an expression that depends on other variables. When these
            variables change, the new position will be recalculated in consequence and
            the stage will move to the new position.
    """

    serial_port: str = attrs.field(converter=str, on_setattr=attrs.setters.convert)
    device_id: int = attrs.field(
        converter=int,
        validator=[attrs.validators.ge(0), attrs.validators.le(255)],
        on_setattr=attrs.setters.pipe(attrs.setters.convert, attrs.setters.validate),
    )
    position: Expression = attrs.field(
        validator=attrs.validators.instance_of(Expression),
        on_setattr=attrs.setters.validate,
    )

    @classmethod
    def default(cls) -> Self:
        return cls(
            remote_server=None,
            serial_port="COM0",
            device_id=0,
            position=Expression("0"),
        )

    @classmethod
    def dump(cls, config: Self):
        return serialization.converters["json"].unstructure(
            config, ElliptecELL14RotationStageConfiguration
        )

    @classmethod
    def load(cls, config: dict[str, Any]) -> Self:
        return serialization.converters["json"].structure(
            config, ElliptecELL14RotationStageConfiguration
        )
