from typing import Literal, assert_never

from caqtus.device import DeviceName, DeviceParameter
from caqtus.shot_compilation import (
    DeviceCompiler,
    SequenceContext,
    DeviceNotUsedException,
    ShotContext,
)
from caqtus.types.parameter import magnitude_in_unit
from caqtus.types.units import Quantity

from ._configuration import (
    SiglentSDG6022XConfiguration,
    ChannelConfiguration,
    SineWaveOutput,
)
from ._runtime import ChannelState, SiglentState, SinWave


class SiglentSDG6022XCompiler(DeviceCompiler):
    def __init__(self, device_name: DeviceName, sequence_context: SequenceContext):
        configuration = sequence_context.get_device_configuration(device_name)
        if not isinstance(configuration, SiglentSDG6022XConfiguration):
            raise TypeError(f"Invalid configuration type for device {device_name}")
        if all(channel == "ignore" for channel in configuration.channels):
            raise DeviceNotUsedException(
                f"Both channels are ignored for device {device_name}"
            )
        self.configuration = configuration

    def compile_initialization_parameters(self):
        return {
            **super().compile_initialization_parameters(),
            DeviceParameter("resource_name"): self.configuration.resource_name,
        }

    def compile_shot_parameters(self, shot_context: ShotContext):
        siglent_state = SiglentState(
            channel_0=compile_channel_state(
                self.configuration.channels[0], shot_context, 0
            ),
            channel_1=compile_channel_state(
                self.configuration.channels[1], shot_context, 1
            ),
        )
        return {
            **super().compile_shot_parameters(shot_context),
            "state": siglent_state,
        }


def compile_channel_state(
    channel_config: ChannelConfiguration, shot_context: ShotContext, channel: int
) -> ChannelState | Literal["ignore"]:
    if channel_config == "ignore":
        return "ignore"
    if isinstance(channel_config, SineWaveOutput):
        return compile_sinewave_output(channel_config, shot_context, channel)
    assert_never(channel_config)


def compile_sinewave_output(
    sine_wave_output: SineWaveOutput, shot_context: ShotContext, channel: int
) -> ChannelState:
    amplitude = sine_wave_output.amplitude.evaluate(shot_context.get_variables())
    if not isinstance(amplitude, Quantity):
        raise TypeError(f"Expected amplitude to be a Quantity, got {type(amplitude)}")
    amplitude_magnitude = magnitude_in_unit(amplitude, "V")

    frequency = sine_wave_output.frequency.evaluate(shot_context.get_variables())
    if not isinstance(frequency, Quantity):
        raise TypeError(f"Expected frequency to be a Quantity, got {type(frequency)}")
    frequency_magnitude = magnitude_in_unit(frequency, "Hz")

    offset = sine_wave_output.offset.evaluate(shot_context.get_variables())
    if not isinstance(offset, Quantity):
        raise TypeError(f"Expected offset to be a Quantity, got {type(offset)}")
    offset_magnitude = magnitude_in_unit(offset, "V")

    return SinWave(
        frequency=frequency_magnitude,
        amplitude=amplitude_magnitude,
        offset=offset_magnitude,
        output_enabled=sine_wave_output.output_enabled,
        load=sine_wave_output.load,
        channel=channel,
    )
