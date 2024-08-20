import contextlib
import decimal
import logging
from functools import singledispatchmethod
from typing import ClassVar, Literal

import attrs.setters
from attrs import define, field
from attrs.setters import frozen
from attrs.validators import instance_of, ge, le
from pulsestreamer import (
    PulseStreamer,
    TriggerStart,
    TriggerRearm,
    Sequence as PulseStreamerSequence,
    OutputState,
    ClockSource,
)

from caqtus.device import RuntimeDevice
from caqtus.device.sequencer import (
    Sequencer,
    TimeStep,
)
from caqtus.device.sequencer.instructions import (
    SequencerInstruction,
    Pattern,
    Concatenated,
    Repeated,
)
from caqtus.device.sequencer.runtime import ProgrammedSequence, SequenceStatus
from caqtus.device.sequencer.trigger import (
    Trigger,
    ExternalTriggerStart,
    TriggerEdge,
    SoftwareTrigger,
)
from caqtus.types.recoverable_exceptions import ConnectionFailedError

logger = logging.getLogger(__name__)


@define(slots=False)
class SwabianPulseStreamer(Sequencer, RuntimeDevice):
    """Device class to program the Swabian Pulse Streamer.

    Attributes:
        ip_address: The IP address of the device.
        time_step: The smallest allowed time step, in nanoseconds.
            The time step is fixed to 1 ns.
        trigger: Indicates how the sequence is started and how it is clocked.
        clock_source: The hardware clock source of the device.
    """

    # only support digital channels at the moment
    channel_number: ClassVar[int] = 8

    ip_address: str = field(validator=instance_of(str), on_setattr=frozen)
    time_step: TimeStep = field(
        validator=[ge(decimal.Decimal(1)), le(decimal.Decimal(1))], on_setattr=frozen
    )

    trigger: Trigger = field(
        factory=lambda: ExternalTriggerStart(edge=TriggerEdge.RISING),
        on_setattr=attrs.setters.frozen,
    )
    clock_source: Literal["internal", "external 10MHz", "external 125MHz"] = field(
        default="external 10MHz", on_setattr=frozen
    )

    _pulse_streamer: PulseStreamer = field(init=False)

    @trigger.validator  # type: ignore
    def _validate_trigger(self, _, value):
        if not isinstance(value, (ExternalTriggerStart, SoftwareTrigger)):
            raise ValueError("Only supports software or external trigger start.")

    def initialize(self) -> None:
        super().initialize()

        # There is no close method for the PulseStreamer class
        self._pulse_streamer = PulseStreamer(self.ip_address)
        try:
            self._pulse_streamer.getFirmwareVersion()
        except IOError as e:
            raise ConnectionFailedError(
                f"Could not connect to swabian pulse streamer at {self.ip_address}"
            ) from e
        self.setup_trigger()
        if self.clock_source == "internal":
            self._pulse_streamer.selectClock(ClockSource.INTERNAL)
        elif self.clock_source == "external 125MHz":
            self._pulse_streamer.selectClock(ClockSource.EXT_125MHZ)
        elif self.clock_source == "external 10MHz":
            self._pulse_streamer.selectClock(ClockSource.EXT_10MHZ)
        else:
            error = ValueError(f"Invalid clock source: {self.clock_source}")
            error.add_note(
                "Clock source must be "
                "'internal', 'external 10MHz' or 'external 125MHz'."
            )
            raise error

    def setup_trigger(self) -> None:
        if isinstance(self.trigger, SoftwareTrigger):
            start = TriggerStart.SOFTWARE
        elif isinstance(self.trigger, ExternalTriggerStart):
            if self.trigger.edge == TriggerEdge.RISING:
                start = TriggerStart.HARDWARE_RISING
            elif self.trigger.edge == TriggerEdge.FALLING:
                start = TriggerStart.HARDWARE_FALLING
            else:
                raise ValueError("Only supports rising or falling edge.")
        else:
            raise ValueError("Only supports software trigger.")
        self._pulse_streamer.setTrigger(start, TriggerRearm.MANUAL)

    def program_sequence(self, sequence: SequencerInstruction) -> ProgrammedSequence:
        seq = self._construct_pulse_streamer_sequence(sequence)
        last_values = sequence[-1]
        enabled_output = [
            channel
            for channel in range(self.channel_number)
            if last_values[f"ch {channel}"]
        ]
        final_state = OutputState(enabled_output, 0.0, 0.0)
        self._pulse_streamer.stream(seq=seq, n_runs=1, final=final_state)
        return _ProgrammedSequence(self._pulse_streamer, self.trigger)

    @singledispatchmethod
    def _construct_pulse_streamer_sequence(
        self, instruction: SequencerInstruction
    ) -> PulseStreamerSequence:
        raise NotImplementedError(
            f"Can't program instruction with type {type(instruction)}."
        )

    @_construct_pulse_streamer_sequence.register
    def _(self, pattern: Pattern) -> PulseStreamerSequence:
        sequence = self._pulse_streamer.createSequence()
        values = pattern.array
        for channel in range(self.channel_number):
            channel_values = values[f"ch {channel}"]
            sequence.setDigital(channel, [(1, v) for v in channel_values])
        return sequence

    @_construct_pulse_streamer_sequence.register
    def _(self, concatenate: Concatenated) -> PulseStreamerSequence:
        instructions = concatenate.instructions
        seq = self._construct_pulse_streamer_sequence(instructions[0])
        for instruction in instructions[1:]:
            seq += self._construct_pulse_streamer_sequence(instruction)
        return seq

    @_construct_pulse_streamer_sequence.register
    def _(self, repeat: Repeated) -> PulseStreamerSequence:
        if len(repeat.instruction) == 1:
            channel_values = repeat.instruction[0]
            seq = self._pulse_streamer.createSequence()
            for channel in range(self.channel_number):
                seq.setDigital(
                    channel,
                    [
                        (
                            repeat.repetitions,
                            channel_values[f"ch {channel}"],
                        )
                    ],
                )
            return seq
        else:
            return (
                self._construct_pulse_streamer_sequence(repeat.instruction)
                * repeat.repetitions
            )


class _ProgrammedSequence(ProgrammedSequence):
    def __init__(
        self,
        pulse_streamer: PulseStreamer,
        trigger: Trigger,
    ):
        self._pulse_streamer = pulse_streamer
        self._trigger = trigger

    @contextlib.contextmanager
    def run(self):
        status = _SequenceStatus(self._pulse_streamer)
        if isinstance(self._trigger, SoftwareTrigger):
            self._pulse_streamer.startNow()
        # Nothing do start if waiting for external trigger
        try:
            yield status
            if not status.is_finished():
                raise RuntimeError(
                    "Run block exited without error before sequence finished"
                )
        finally:
            self._pulse_streamer.forceFinal()


class _SequenceStatus(SequenceStatus):
    def __init__(self, pulse_streamer: PulseStreamer):
        self._pulse_streamer = pulse_streamer

    def is_finished(self) -> bool:
        return self._pulse_streamer.hasFinished()
