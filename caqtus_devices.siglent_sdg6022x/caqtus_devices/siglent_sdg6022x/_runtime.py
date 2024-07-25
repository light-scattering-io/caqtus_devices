import abc
import contextlib
import logging
from typing import Self, Literal, Optional

import attrs
import caqtus.formatter as fmt
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
    def apply(self, instr: pyvisa.resources.Resource) -> None:
        self.set_output(instr)

    def prefix(self) -> str:
        return f"C{self.channel + 1}:"

    def set_output(self, instr: pyvisa.resources.Resource) -> None:
        load = "HZ" if self.load == "High Z" else f"{self.load}"
        polarity = "NORM"
        output = "ON" if self.output_enabled else "OFF"
        command = f"{self.prefix()}OUTP {output},LOAD,{load},PLRT,{polarity}"
        logger.debug("Sending command %r", command)
        instr.write(command)


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

    def apply(self, instr: pyvisa.resources.Resource) -> None:
        for command in self.commands():
            logger.debug("Sending command %r", command)
            instr.write(command)
        super().apply(instr)

    def commands(self) -> list[str]:
        base_wave_commands = [
            f"{self.prefix()}BSWV WVTP,SINE",
            f"{self.prefix()}BSWV FRQ,{self.frequency}",
            f"{self.prefix()}BSWV AMP,{self.amplitude}",
            f"{self.prefix()}BSWV OFST,{self.offset}",
        ]

        if self.modulation is None:
            return base_wave_commands + [f"{self.prefix()}ModulateWave STATE,OFF"]

        if isinstance(self.modulation, FSKModulation):
            modulation_commands = [
                f"{self.prefix()}ModulateWave FSK",
                f"{self.prefix()}ModulateWave STATE,ON",
                f"{self.prefix()}ModulateWave FSK,HFREQ,{self.modulation.hop_frequency}",
            ]
            return base_wave_commands + modulation_commands

        raise NotImplementedError


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
