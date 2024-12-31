import contextlib
import decimal
import logging
from collections.abc import Sequence, Mapping
from enum import IntFlag
from functools import singledispatchmethod
from typing import ClassVar

import attrs.validators
from attrs import define, field
from attrs.setters import frozen
from attrs.validators import instance_of

from caqtus.device import RuntimeDevice
from caqtus.device.sequencer import Sequencer, TimeStep
from caqtus.device.sequencer.runtime import ProgrammedSequence, SequenceStatus
from caqtus.device.sequencer.trigger import Trigger, SoftwareTrigger
from caqtus.shot_compilation.timed_instructions import (
    TimedInstruction,
    Pattern,
    Repeated,
    Concatenated,
)
from caqtus.types.recoverable_exceptions import ConnectionFailedError
from caqtus.utils import log_exception

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


class SpincoreStatus(IntFlag):
    Stopped = 2**0
    Reset = 2**1
    Running = 2**2
    Waiting = 2**3


@define(slots=False)
class SpincorePulseBlaster(Sequencer, RuntimeDevice):
    """

    Fields:
        clock_cycle: Duration of a clock cycle in ns
        time_step: Digitization time in ns

        board_number: The number used to refer to a given spincore pulseblaster.
        If there are multiple boards connected to the computer, they are numbered from
        0 to n-1.
        spincore_lib_debug: If True, the spincore library will log debug messages in a
            file in the current working directory.
            This can be useful to debug the program, but generates large files.
        time_step: The time step of the sequencer in nanoseconds.
        trigger: Indicates how the sequence is started and how it is clocked.
            Only SoftwareTrigger is supported at the moment.
    """

    channel_number: ClassVar[int] = 24
    clock_cycle: ClassVar[int] = 10

    time_step: TimeStep = field(converter=decimal.Decimal, on_setattr=frozen)
    board_number: int = field(default=0, validator=instance_of(int), on_setattr=frozen)
    spincore_lib_debug: bool = field(
        default=False, validator=instance_of(bool), on_setattr=frozen
    )

    trigger: Trigger = field(
        factory=SoftwareTrigger,
        validator=attrs.validators.instance_of(Trigger),
        on_setattr=frozen,
    )

    @time_step.validator  # type: ignore
    def _validate_time_step(self, _, value):
        div, mod = divmod(value, self.clock_cycle)
        if mod != 0:
            raise ValueError(
                f"Time step ({value}) must be a multiple of the clock cycle "
                f"({self.clock_cycle})."
            )
        if not div >= 5:
            raise ValueError(
                f"Time step ({value}) must be at least 5 times the clock cycle "
                f"({self.clock_cycle})."
            )

    @trigger.validator  # type: ignore
    def _validate_trigger(self, _, value):
        if not isinstance(value, SoftwareTrigger):
            raise NotImplementedError(
                f"Trigger type {type(value)} is not implemented for the Spincore "
                f"PulseBlaster"
            )
        return value

    @log_exception(logger)
    def initialize(self) -> None:
        super().initialize()

        from . import spinapi

        self._spinapi = spinapi

        self._spinapi.pb_set_debug(self.spincore_lib_debug)

        board_count = self._spinapi.pb_count_boards()
        if self.board_number >= board_count:
            raise ConnectionFailedError(
                f"Can't access board {self.board_number}\nThere are only"
                f" {board_count} boards"
            )
        if self._spinapi.pb_select_board(self.board_number) != 0:
            raise ConnectionFailedError(
                f"Can't access board {self.board_number}: "
                f"{self._spinapi.pb_get_error()}"
            )

        if self._spinapi.pb_init() != 0:
            raise ConnectionFailedError(
                f"Can't initialize board {self.board_number}: "
                f"{self._spinapi.pb_get_error()}"
            )
        self._add_closing_callback(self._spinapi.pb_close)

        self._spinapi.pb_core_clock(1e3 / self.clock_cycle)

    def program_sequence(self, sequence: TimedInstruction) -> ProgrammedSequence:
        spinapi = self._spinapi
        if spinapi.pb_start_programming(spinapi.PULSE_PROGRAM) != 0:
            raise RuntimeError(
                f"Can't start programming sequence.{spinapi.pb_get_error()}"
            )

        self._program_instruction(sequence)
        self.program_stop(sequence[-1])

        if spinapi.pb_stop_programming() != 0:
            raise RuntimeError(
                "An error occurred when finishing programming the sequence."
                f"{spinapi.pb_get_error()}"
            )
        return _ProgrammedSequence(spinapi)

    @singledispatchmethod
    def _program_instruction(self, instruction: TimedInstruction) -> int:
        raise NotImplementedError(
            f"Can't program instruction with type {type(instruction)}"
        )

    @_program_instruction.register
    @log_exception(logger)
    def _(self, pattern: Pattern):
        for i in range(len(pattern)):
            values = pattern[i]
            outputs = [
                values[f"ch {channel}"] for channel in range(self.channel_number)
            ]
            self._program_continue(outputs, 1)

    @property
    def max_number_ticks(self) -> int:
        cycles_per_step = int(self.time_step / self.clock_cycle)
        return int((2**32 - 1) / cycles_per_step)

    @property
    def max_duration(self) -> float:
        return self.max_number_ticks * self._time_step * self._spinapi.ns

    @property
    def _time_step(self) -> int:
        # We know that the time step is a multiple of the clock cycle, so it is an
        # integer, and we can safely case it.
        return int(self.time_step)

    def _program_continue(self, output_: Sequence[bool], number_ticks: int):
        spinapi = self._spinapi
        # break the duration into multiple long waits and one short wait
        number_of_repetitions, remainder = divmod(number_ticks, self.max_number_ticks)

        flags = self._output_to_flags(output_)
        if number_of_repetitions >= 1:
            # Delay multiplier must be greater than 2, so we divide by 2 the length of
            # the wait and multiply the number of repetitions by 2
            if (
                spinapi.pb_inst_pbonly(
                    flags,
                    spinapi.Inst.LONG_DELAY,
                    2 * number_of_repetitions,
                    self.max_duration / 2,
                )
                < 0
            ):
                raise RuntimeError(
                    "An error occurred when programming a long delay of duration"
                    f" {self.max_duration / 2} s with"
                    f" {2*number_of_repetitions} repetitions. "
                )
        duration = remainder * self._time_step * spinapi.ns
        if spinapi.pb_inst_pbonly(flags, spinapi.Inst.CONTINUE, 0, duration) < 0:
            raise RuntimeError(
                "An error occurred when programming a continue instruction with"
                f" duration {duration} s."
            )

    @_program_instruction.register
    @log_exception(logger)
    def _(self, repeat: Repeated):
        spinapi = self._spinapi
        if len(repeat.instruction) == 1:
            channel_values = repeat.instruction.to_pattern()[0]
            outputs = [
                channel_values[f"ch {channel}"]
                for channel in range(self.channel_number)
            ]
            self._program_continue(outputs, repeat.repetitions)
            return
        else:
            for_part = repeat.instruction[0]
            middle = repeat.instruction[1:-1]
            end_for_part = repeat.instruction[-1]
            rep = repeat.repetitions
        for_flag = self._output_to_flags(
            [for_part[f"ch {channel}"] for channel in range(self.channel_number)]
        )
        end_for_flag = self._output_to_flags(
            [end_for_part[f"ch {channel}"] for channel in range(self.channel_number)]
        )
        logger.debug(f"for {rep=}")
        if rep > 2**20 - 1:
            raise ValueError(
                f"Can't program a for loop with more than {2**20 - 1} repetitions."
            )
        if (
            loop_beginning := spinapi.pb_inst_pbonly(
                for_flag, spinapi.Inst.LOOP, rep, self._time_step * spinapi.ns
            )
        ) < 0:
            raise RuntimeError(
                "An error occurred when programming the sequence."
                f"{spinapi.pb_get_error()}"
            )
        if len(middle) > 0:
            self._program_instruction(middle)

        if (
            spinapi.pb_inst_pbonly(
                end_for_flag,
                spinapi.Inst.END_LOOP,
                loop_beginning,
                self._time_step * spinapi.ns,
            )
            < 0
        ):
            raise RuntimeError(
                "An error occurred when programming the sequence."
                f"{spinapi.pb_get_error()}"
            )

    @_program_instruction.register
    @log_exception(logger)
    def _(self, concatenate: Concatenated):
        for instruction in concatenate.instructions:
            self._program_instruction(instruction)

    def program_stop(self, pattern: Mapping[str, bool]):
        spinapi = self._spinapi
        outputs = [pattern[f"ch {channel}"] for channel in range(self.channel_number)]
        flags = self._output_to_flags(outputs)
        if (
            spinapi.pb_inst_pbonly(
                flags, spinapi.Inst.STOP, 0, self._time_step * spinapi.ns
            )
            < 0
        ):
            raise RuntimeError(
                "An error occurred when programming the sequence. "
                f"{spinapi.pb_get_error()}"
            )

    def _output_to_flags(self, states: Sequence[bool]) -> int:
        flags = 0
        for channel, state in zip(range(self.channel_number), states, strict=True):
            flags |= int(state) << channel
        return flags


class _ProgrammedSequence(ProgrammedSequence):
    def __init__(self, spinapi):
        self._spinapi = spinapi

    @contextlib.contextmanager
    def run(self):
        spinapi = self._spinapi
        if spinapi.pb_reset() != 0:
            raise RuntimeError(f"Can't reset the board. {spinapi.pb_get_error()}")

        if spinapi.pb_start() != 0:
            raise RuntimeError(f"Can't start the sequence. {spinapi.pb_get_error()}")
        status = _SequenceStatus(spinapi)
        try:
            yield status
            if not status.is_finished():
                while not status.is_finished():
                    pass
                raise RuntimeError("Run block exited before the sequence finished")
        finally:
            if spinapi.pb_stop() != 0:
                raise RuntimeError(
                    f"Error when stopping the sequence. {spinapi.pb_get_error()}"
                )


class _SequenceStatus(SequenceStatus):
    def __init__(self, spinapi):
        self._spinapi = spinapi

    def is_finished(self) -> bool:
        spinapi = self._spinapi
        is_running = spinapi.pb_read_status() & SpincoreStatus.Running
        return not is_running
