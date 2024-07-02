import abc
import contextlib
import logging
from typing import Self, Literal

import attrs
import pyvisa
import pyvisa.constants
from caqtus.device import Device

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

    def apply(self, instr: pyvisa.resources.Resource) -> None:
        for command in self.commands():
            logger.debug("Sending command %r", command)
            instr.write(command)
        super().apply(instr)

    def commands(self) -> list[str]:
        return [
            f"{self.prefix()}BSWV WVTP,SINE",
            f"{self.prefix()}BSWV FRQ,{self.frequency}",
            f"{self.prefix()}BSWV AMP,{self.amplitude}",
            f"{self.prefix()}BSWV OFST,{self.offset}",
        ]


@attrs.frozen
class SiglentState:
    """State of a Siglent SDG6022X arbitrary waveform generator."""

    channel_0: ChannelState | Literal["ignore"] = attrs.field(
        validator=attrs.validators.instance_of(ChannelState)
    )
    channel_1: ChannelState | Literal["ignore"] = attrs.field(
        validator=attrs.validators.instance_of(ChannelState)
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
        try:
            self._resource_manager = self._exit_stack.enter_context(
                contextlib.closing(pyvisa.ResourceManager())
            )
            logger.info("Acquired VISA resource manager")
            self._instr = self._exit_stack.enter_context(
                contextlib.closing(
                    self._resource_manager.open_resource(
                        self._resource_name,
                        access_mode=pyvisa.constants.AccessModes.exclusive_lock,
                    )
                )
            )
            logger.info("Connected to %s", self._resource_name)
            device_identification = self._instr.query("*IDN?")
            logger.info("Device identification: %s", device_identification)
        except:
            self._exit_stack.close()
            raise
        return self

    def update_state(self, state: SiglentState) -> None:
        state.apply(self._instr)

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._exit_stack.__exit__(exc_type, exc_val, exc_tb)

    def write_command(self, command: str) -> None:
        self._instr.write(command)
