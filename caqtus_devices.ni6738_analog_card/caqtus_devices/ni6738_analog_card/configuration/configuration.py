from __future__ import annotations

import decimal
from typing import ClassVar, Type

import attrs

from caqtus.device.sequencer import (
    SequencerConfiguration,
    AnalogChannelConfiguration,
    TimeStep,
)
from caqtus.device.sequencer import converter
from caqtus.device.sequencer.channel_commands import Constant
from caqtus.device.sequencer.trigger import SoftwareTrigger
from caqtus.types.expression import Expression
from ..runtime import NI6738AnalogCard


@attrs.define
class NI6738SequencerConfiguration(SequencerConfiguration[NI6738AnalogCard]):
    @classmethod
    def channel_types(cls) -> tuple[Type[AnalogChannelConfiguration], ...]:
        return (AnalogChannelConfiguration,) * cls.number_channels

    number_channels: ClassVar[int] = 32
    device_id: str = attrs.field(converter=str, on_setattr=attrs.setters.convert)
    channels: tuple[AnalogChannelConfiguration, ...] = attrs.field(
        converter=tuple,
        validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(AnalogChannelConfiguration)
        ),
        on_setattr=attrs.setters.pipe(attrs.setters.convert, attrs.setters.validate),
    )
    time_step: TimeStep = attrs.field(
        default=decimal.Decimal(2500),
        converter=decimal.Decimal,
        validator=attrs.validators.ge(decimal.Decimal(2500)),
        on_setattr=attrs.setters.pipe(attrs.setters.convert, attrs.setters.validate),
    )

    @channels.validator  # type: ignore
    def validate_channels(self, attribute, channels: list[AnalogChannelConfiguration]):
        super().validate_channels(attribute, channels)
        for channel in channels:
            if channel.output_unit != "V":
                raise ValueError(
                    f"Channel {channel} output units ({channel.output_unit}) are not"
                    " compatible with Volt"
                )

    @classmethod
    def dump(cls, obj: NI6738SequencerConfiguration):
        return converter.unstructure(obj, NI6738SequencerConfiguration)

    @classmethod
    def load(cls, data) -> NI6738SequencerConfiguration:
        return converter.structure(data, NI6738SequencerConfiguration)

    @classmethod
    def default(cls) -> NI6738SequencerConfiguration:
        return cls(
            remote_server=None,
            trigger=SoftwareTrigger(),
            device_id="Dev1",
            channels=tuple(
                AnalogChannelConfiguration(
                    description="", output_unit="V", output=Constant(Expression("0 V"))
                )
                for _ in range(cls.number_channels)
            ),
        )
