from __future__ import annotations

import decimal
from typing import ClassVar, Type

import attrs

from caqtus.device.sequencer import (
    SequencerConfiguration,
    ChannelConfiguration,
    DigitalChannelConfiguration,
    TimeStep,
)
from caqtus.device.sequencer.trigger import SoftwareTrigger
from caqtus.device.sequencer import converter
from caqtus.device.sequencer.channel_commands import Constant
from caqtus.types.expression import Expression
from ..runtime import SpincorePulseBlaster


@attrs.define
class SpincoreSequencerConfiguration(SequencerConfiguration[SpincorePulseBlaster]):
    """Holds the static configuration of a spincore sequencer device.

    Attributes:
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
    time_step: TimeStep = attrs.field(
        default=decimal.Decimal(50),
        converter=decimal.Decimal,
        on_setattr=attrs.setters.pipe(attrs.setters.convert, attrs.setters.validate),
    )

    clock_cycle: ClassVar[int] = 10

    @time_step.validator  # type: ignore
    def _validate_time_step(self, _, value):
        div, mod = divmod(value, self.clock_cycle)
        if mod != 0:
            raise ValueError(
                f"Time step ({value}) must be a multiple of the clock cycle " f"(10)."
            )
        if not div >= 5:
            raise ValueError(
                f"Time step ({value}) must be at least 5 times the clock cycle "
                f"({self.clock_cycle})."
            )

    @classmethod
    def dump(cls, configuration: SpincoreSequencerConfiguration):
        return converter.unstructure(configuration, SpincoreSequencerConfiguration)

    @classmethod
    def load(cls, data) -> SpincoreSequencerConfiguration:
        return converter.structure(data, SpincoreSequencerConfiguration)

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
