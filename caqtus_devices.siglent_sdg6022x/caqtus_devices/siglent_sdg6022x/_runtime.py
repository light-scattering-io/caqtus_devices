import abc
import contextlib
import logging
import re
from typing import Self, Literal, Optional

import attrs
import caqtus.formatter as fmt
import numpy as np
import pyvisa
import pyvisa.constants
from caqtus.device import Device
from caqtus.types.recoverable_exceptions import ConnectionFailedError
from caqtus.utils.contextlib import close_on_error

logger = logging.getLogger(__name__)


@attrs.frozen
class ChannelState(abc.ABC):
    channel: int
    output_enabled: bool = attrs.field(validator=attrs.validators.instance_of(bool))
    load: float | Literal["High Z"] = attrs.field(
        validator=attrs.validators.in_([50, "High Z"])
    )

    @abc.abstractmethod
    def apply(self, instr: pyvisa.resources.TCPIPInstrument) -> None:
        if self.should_update_output(instr):
            load = "HZ" if self.load == "High Z" else f"{self.load}"
            polarity = "NORM"
            output = "ON" if self.output_enabled else "OFF"
            command = f"OUTP {output},LOAD,{load},PLRT,{polarity}"
            self.write(instr, command)

    def write(self, instr: pyvisa.resources.TCPIPInstrument, command: str) -> None:
        logger.debug("Sending command %r", command)
        instr.write(f"{self.prefix()}{command}")

    def prefix(self) -> str:
        return f"C{self.channel + 1}:"

    def should_update_output(self, instr: pyvisa.resources.TCPIPInstrument) -> bool:
        query = instr.query(f"{self.prefix()}OUTP?")
        current_output = self.parse_output(query)

        return not all(
            [
                current_output["state"] == ("ON" if self.output_enabled else "OFF"),
                current_output["load"] == ("50" if self.load == 50 else "HZ"),
                current_output["polarity"] == "NOR",
            ]
        )

    @staticmethod
    def parse_output(out: str) -> dict[str, str]:
        pattern = re.compile(
            r"C(?P<channel>\d):OUTP (?P<state>ON|OFF),"
            r"LOAD,(?P<load>50|HZ),"
            r"POWERON_STATE,0,"
            r"PLRT,(?P<polarity>NOR|INV)"
        )

        match = pattern.match(out)

        if match:
            return match.groupdict()
        else:
            raise ValueError(f"Could not parse output: {out}")


@attrs.frozen
class FSKModulation:
    hop_frequency: float = attrs.field(converter=float)


@attrs.frozen
class SinWave(ChannelState):
    """
    Attributes:
        frequency: The frequency of the sine wave in Hz.
        amplitude: Peak-to-peak amplitude of the sine wave in V.
        offset: The DC offset of the sine wave in V.
    """

    frequency: float = attrs.field(converter=float)
    amplitude: float = attrs.field(converter=float)
    offset: float = attrs.field(converter=float)
    modulation: Optional[FSKModulation]

    def apply(self, instr: pyvisa.resources.TCPIPInstrument):
        old_params = BaseWaveStatus.from_string(instr.query(f"{self.prefix()}BSWV?"))
        logger.debug("Old base wave parameters: %s", old_params)

        if not old_params.channel == self.channel + 1:
            raise RuntimeError(
                f"Expected channel {self.channel + 1}, got {old_params.channel}"
            )

        if old_params.wave_type != "SINE":
            self.write(instr, f"BSWV WVTP,SINE")

        # We use numpy.isclose to compare floating point numbers instead of
        # math.isclose because the latter does not have an absolute tolerance by
        # default, which makes it unsuitable for comparison with 0.
        if not np.isclose(old_params.frequency, self.frequency):
            self.write(instr, f"BSWV FRQ,{self.frequency}")

        if not np.isclose(old_params.amplitude, self.amplitude):
            self.write(instr, f"BSWV AMP,{self.amplitude}")

        if not np.isclose(old_params.offset, self.offset):
            self.write(instr, f"BSWV OFST,{self.offset}")

        new_params = BaseWaveStatus.from_string(instr.query(f"{self.prefix()}BSWV?"))
        logger.debug("New base wave parameters: %s", new_params)

        if not new_params.channel == self.channel + 1:
            raise RuntimeError(
                f"Expected channel {self.channel + 1}, got {new_params.channel}"
            )

        if new_params.wave_type != "SINE":
            raise ValueError(f"Failed to set wave type: {new_params}")

        if not np.isclose(new_params.frequency, self.frequency):
            raise ValueError(f"Failed to set frequency: {new_params}")

        if not np.isclose(new_params.amplitude, self.amplitude):
            raise ValueError(f"Failed to set amplitude: {new_params}")

        if not np.isclose(new_params.offset, self.offset):
            raise ValueError(f"Failed to set offset: {new_params}")

        if self.modulation is None:
            return super().apply(instr)
        else:
            raise NotImplementedError("Modulation not implemented")

        # if isinstance(self.modulation, FSKModulation):
        #     modulation_commands = [
        #         f"{self.prefix()}ModulateWave FSK",
        #         f"{self.prefix()}ModulateWave STATE,ON",
        #         f"{self.prefix()}ModulateWave FSK,SRC,EXT",
        #         f"{self.prefix()}ModulateWave FSK,HFRQ,{self.modulation.hop_frequency}",
        #     ]
        #     return base_wave_commands + modulation_commands


@attrs.frozen
class BaseWaveStatus:
    channel: int = attrs.field(converter=int)
    wave_type: str = attrs.field(converter=str)
    frequency: float = attrs.field(converter=float)
    amplitude: float = attrs.field(converter=float)
    max_output_amplitude: float = attrs.field(converter=float)
    offset: float = attrs.field(converter=float)
    phase: float = attrs.field(converter=float)

    @classmethod
    def from_string(cls, base_wave: str) -> Self:
        RE_FLOAT = r"[+\-]?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+\-]?\d+)?"
        pattern = re.compile(
            r"C(?P<channel>\d):BSWV WVTP,(?P<wave_type>\w+),"
            rf"FRQ,(?P<frequency>{RE_FLOAT})HZ,"
            rf"PERI,{RE_FLOAT}S,"
            rf"AMP,(?P<amplitude>{RE_FLOAT})V,"
            rf"AMPVRMS,{RE_FLOAT}Vrms,"
            rf"AMPDBM,{RE_FLOAT}dBm,"
            rf"MAX_OUTPUT_AMP,(?P<max_output_amplitude>{RE_FLOAT})V,"
            rf"OFST,(?P<offset>{RE_FLOAT})V,"
            rf"HLEV,{RE_FLOAT}V,"
            rf"LLEV,{RE_FLOAT}V,"
            rf"PHSE,(?P<phase>{RE_FLOAT})"
        )

        match = pattern.match(base_wave)

        if match:
            return cls(**match.groupdict())
        else:
            raise ValueError(f"Could not parse base wave: {base_wave}")


def _channel_validator(instance, attribute, value):
    if value == "ignore":
        return
    if isinstance(value, ChannelState):
        return
    raise ValueError(f"Expected ChannelState or 'ignore', got {value!r}")


@attrs.frozen
class SiglentState:
    """State of a Siglent SDG6022X arbitrary waveform generator."""

    channel_0: ChannelState | Literal["ignore"] = attrs.field(
        validator=_channel_validator
    )
    channel_1: ChannelState | Literal["ignore"] = attrs.field(
        validator=_channel_validator
    )

    def apply(self, instr: pyvisa.resources.Resource) -> None:
        if self.channel_0 != "ignore":
            self.channel_0.apply(instr)
        if self.channel_1 != "ignore":
            self.channel_1.apply(instr)


class SiglentSDG6022X(Device):
    """Siglent SDG6022X arbitrary waveform generator.

    Args:
        resource_name: The VISA resource name of the device.
    """

    def __init__(self, resource_name: str):
        self._resource_name = resource_name

        self._exit_stack = contextlib.ExitStack()
        self._resource_manager: pyvisa.ResourceManager
        self._instr: pyvisa.resources.Resource

    def __enter__(self) -> Self:
        with close_on_error(self._exit_stack):
            self._resource_manager = self._exit_stack.enter_context(
                contextlib.closing(pyvisa.ResourceManager())
            )
            logger.info("Acquired VISA resource manager")
            try:
                self._instr = self._exit_stack.enter_context(
                    contextlib.closing(
                        self._resource_manager.open_resource(
                            self._resource_name,
                            access_mode=pyvisa.constants.AccessModes.exclusive_lock,
                        )
                    )
                )
            except pyvisa.errors.VisaIOError as e:
                raise ConnectionFailedError(
                    f"Failed to connect to siglent SDG6022X with "
                    f"{fmt.device_param('resource name', self._resource_name)}"
                ) from e
            logger.info("Connected to %s", self._resource_name)
            device_identification = self._instr.query("*IDN?")
            logger.info("Device identification: %s", device_identification)
            return self

    def update_state(self, state: SiglentState) -> None:
        state.apply(self._instr)

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._exit_stack.__exit__(exc_type, exc_val, exc_tb)

    def write_command(self, command: str) -> None:
        self._instr.write(command)
