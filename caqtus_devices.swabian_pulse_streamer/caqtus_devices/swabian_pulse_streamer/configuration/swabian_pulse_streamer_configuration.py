from typing import ClassVar, Self

import attrs
from caqtus.device.sequencer import (
    SequencerConfiguration,
    DigitalChannelConfiguration,
)
from caqtus.device.sequencer.configuration import Constant
from caqtus.device.sequencer.trigger import SoftwareTrigger
from caqtus.types.expression import Expression
from caqtus.utils import serialization

from ..runtime import SwabianPulseStreamer


@attrs.define
class SwabianPulseStreamerConfiguration(SequencerConfiguration[SwabianPulseStreamer]):
    number_channels: ClassVar[int] = 8

    ip_address: str = attrs.field(converter=str, on_setattr=attrs.setters.convert)

    channels: tuple[DigitalChannelConfiguration, ...] = attrs.field(
        converter=tuple,
        validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(DigitalChannelConfiguration)
        ),
        on_setattr=attrs.setters.pipe(attrs.setters.convert, attrs.setters.validate),
    )

    @classmethod
    def channel_types(cls) -> tuple[type[DigitalChannelConfiguration], ...]:
        return (DigitalChannelConfiguration,) * cls.number_channels

    @classmethod
    def dump(cls, config: Self) -> serialization.JSON:
        return serialization.converters["json"].unstructure(config, cls)

    @classmethod
    def load(cls, data: serialization.JSON) -> Self:
        return serialization.converters["json"].structure(data, cls)

    @classmethod
    def default(cls) -> Self:
        return SwabianPulseStreamerConfiguration(
            remote_server=None,
            time_step=1,
            trigger=SoftwareTrigger(),
            ip_address="...",
            channels=tuple(
                DigitalChannelConfiguration(
                    description="", output=Constant(Expression("Disabled"))
                )
                for _ in range(cls.number_channels)
            ),
        )
