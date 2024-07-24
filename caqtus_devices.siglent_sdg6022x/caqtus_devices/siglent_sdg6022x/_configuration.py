from __future__ import annotations

from typing import Literal, Self, Optional

import attrs
from caqtus.device import DeviceConfiguration
from caqtus.device.output_transform import (
    EvaluableOutput,
    converter,
    structure_evaluable_output,
)
from caqtus.device.output_transform.transformation import evaluable_output_validator
from caqtus.types.expression import Expression
from caqtus.utils import serialization

from ._runtime import SiglentSDG6022X


@attrs.define
class SineWaveOutput:
    """Holds the configuration for a channel that outputs a sine wave.

    Attributes:
        frequency: The frequency of the sine wave. Must be compatible with frequency.
        amplitude: Peak-to-peak amplitude of the sine wave.
        offset: The DC offset of the sine wave.
    """

    output_enabled: bool = attrs.field(converter=bool, on_setattr=attrs.setters.convert)
    load: float | Literal["High Z"] = attrs.field(
        validator=attrs.validators.in_([50.0, "High Z"]),
        on_setattr=attrs.setters.validate,
    )
    frequency: EvaluableOutput = attrs.field(validator=evaluable_output_validator)
    amplitude: EvaluableOutput = attrs.field(validator=evaluable_output_validator)
    offset: EvaluableOutput = attrs.field(validator=evaluable_output_validator)

    @classmethod
    def default(cls) -> SineWaveOutput:
        return cls(
            output_enabled=True,
            load=50.0,
            frequency=Expression("1 kHz"),
            amplitude=Expression("1 V"),
            offset=Expression("0 V"),
        )


ChannelConfiguration = SineWaveOutput | Literal["ignore"]


@attrs.define
class SiglentSDG6022XConfiguration(DeviceConfiguration[SiglentSDG6022X]):
    """Configuration for the Siglent SDG6022X AWG.

    Attributes:
        resource_name: The VISA resource name of the device.
        channels: The configuration for the two output channels.
    """

    resource_name: str = attrs.field(converter=str, on_setattr=attrs.setters.convert)
    channels: tuple[ChannelConfiguration, ChannelConfiguration] = attrs.field()

    @classmethod
    def default(cls) -> SiglentSDG6022XConfiguration:
        return cls(
            remote_server=None,
            resource_name="",
            channels=(SineWaveOutput.default(), SineWaveOutput.default()),
        )

    @classmethod
    def load(cls, data: serialization.JSON) -> Self:
        return structure_siglent_configuration(data, cls)

    def dump(self) -> serialization.JSON:
        return _converter.unstructure(self)


def structure_siglent_configuration(data, _):
    return SiglentSDG6022XConfiguration(
        remote_server=_converter.structure(data["remote_server"], Optional[str]),
        resource_name=_converter.structure(data["resource_name"], str),
        channels=(
            structure_channel_configuration(data["channels"][0], ChannelConfiguration),
            structure_channel_configuration(data["channels"][1], ChannelConfiguration),
        ),
    )


_converter = converter


def unstructure_channel_configuration(obj: ChannelConfiguration) -> serialization.JSON:
    if obj == "ignore":
        return "ignore"
    if isinstance(obj, SineWaveOutput):
        return _converter.unstructure(obj) | {"_type": "SineWaveOutput"}
    raise ValueError(f"Unknown channel configuration: {obj!r}")


def structure_channel_configuration(
    serialized: serialization.JSON, _
) -> ChannelConfiguration:
    if serialized == "ignore":
        return "ignore"
    if isinstance(serialized, dict):
        if serialized.pop("_type") == "SineWaveOutput":
            return structure_sine_wave_output(serialized, SineWaveOutput)
    raise ValueError(f"Unknown channel configuration: {serialized!r}")


def structure_sine_wave_output(data: serialization.JSON, _):
    return SineWaveOutput(
        output_enabled=_converter.structure(data["output_enabled"], bool),
        load=_converter.structure(data["load"], float | Literal["High Z"]),
        frequency=structure_evaluable_output(data["frequency"], EvaluableOutput),
        amplitude=structure_evaluable_output(data["amplitude"], EvaluableOutput),
        offset=structure_evaluable_output(data["offset"], EvaluableOutput),
    )


# # Workaround for https://github.com/python-attrs/cattrs/issues/430
# structure_hook = cattrs.gen.make_dict_structure_fn(
#     SineWaveOutput,
#     _converter,
#     frequency=cattrs.override(struct_hook=structure_evaluable_output),
#     amplitude=cattrs.override(struct_hook=structure_evaluable_output),
#     offset=cattrs.override(struct_hook=structure_evaluable_output),
# )

# _converter.register_structure_hook(SineWaveOutput, structure_sine_wave_output)
#
# _converter.register_structure_hook(
#     ChannelConfiguration, structure_channel_configuration
# )
_converter.register_unstructure_hook(
    ChannelConfiguration, unstructure_channel_configuration
)
