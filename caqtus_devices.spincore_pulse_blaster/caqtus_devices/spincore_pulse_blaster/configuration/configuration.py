from __future__ import annotations

from typing import ClassVar, Type

import attrs
from caqtus.device.sequencer import (
    SequencerConfiguration,
    ChannelConfiguration,
    DigitalChannelConfiguration,
    SoftwareTrigger,
)
from caqtus.device.sequencer.configuration import Constant
from caqtus.types.expression import Expression
from caqtus.utils import serialization

from ..runtime import SpincorePulseBlaster


@attrs.define
class SpincoreSequencerConfiguration(SequencerConfiguration[SpincorePulseBlaster]):
    """Holds the static configuration of a spincore sequencer device.

    Fields:
        board_number: The number of the board to use. With only one board connected,
            this number is usually 0.
        time_step: The quantization time step used. All times during a run are multiples
            of this value.
    """

    @classmethod
    def channel_types(cls) -> tuple[Type[ChannelConfiguration], ...]:
        return (DigitalChannelConfiguration,) * cls.number_channels

    number_channels: ClassVar[int] = 24

    board_number: int = attrs.field(
        converter=int,
        on_setattr=attrs.setters.convert,
    )
    channels: tuple[DigitalChannelConfiguration, ...] = attrs.field(
        converter=tuple,
        validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(DigitalChannelConfiguration)
        ),
        on_setattr=attrs.setters.pipe(attrs.setters.convert, attrs.setters.validate),
    )
    time_step: int = attrs.field(
        default=50,
        converter=int,
        validator=attrs.validators.ge(50),
        on_setattr=attrs.setters.pipe(attrs.setters.convert, attrs.setters.validate),
    )

    @classmethod
    def dump(cls, configuration: SpincoreSequencerConfiguration) -> serialization.JSON:
        return serialization.unstructure(configuration, SpincoreSequencerConfiguration)

    @classmethod
    def load(cls, data) -> SpincoreSequencerConfiguration:
        return serialization.structure(data, SpincoreSequencerConfiguration)

    @classmethod
    def default(cls) -> SpincoreSequencerConfiguration:
        return SpincoreSequencerConfiguration(
            remote_server=None,
            board_number=0,
            time_step=50,
            channels=tuple(
                [
                    DigitalChannelConfiguration(
                        description=f"Channel {channel}",
                        output=Constant(Expression("Disabled")),
                    )
                    for channel in range(SpincoreSequencerConfiguration.number_channels)
                ]
            ),
            trigger=SoftwareTrigger(),
        )
