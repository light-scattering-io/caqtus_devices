from __future__ import annotations

from typing import Literal, Self

import attrs
from caqtus.device import DeviceConfiguration
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
    frequency: Expression = attrs.field(
        validator=attrs.validators.instance_of(Expression)
    )
    amplitude: Expression = attrs.field(
        validator=attrs.validators.instance_of(Expression)
    )
    offset: Expression = attrs.field(validator=attrs.validators.instance_of(Expression))

    @classmethod
    def default(cls) -> SineWaveOutput:
        return cls(
            output_enabled=True,
            load=50.0,
            frequency=Expression("1 kHz"),
            amplitude=Expression("1 V"),
            offset=Expression("0 V"),
        )


ChannelConfiguration = Literal["ignore"] | SineWaveOutput


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
        return converter.structure(data, cls)

    def dump(self) -> serialization.JSON:
        return converter.unstructure(self)


converter = serialization.copy_converter()


def unstructure_channel_configuration(obj: ChannelConfiguration) -> serialization.JSON:
    if obj == "ignore":
        return "ignore"
    if isinstance(obj, SineWaveOutput):
        return converter.unstructure(obj) | {"_type": "SineWaveOutput"}
    raise ValueError(f"Unknown channel configuration: {obj!r}")


def structure_channel_configuration(
    serialized: serialization.JSON, _
) -> ChannelConfiguration:
    if serialized == "ignore":
        return "ignore"
    if isinstance(serialized, dict):
        if serialized.pop("_type") == "SineWaveOutput":
            return converter.structure(serialized, SineWaveOutput)
    raise ValueError(f"Unknown channel configuration: {serialized!r}")


converter.register_structure_hook(ChannelConfiguration, structure_channel_configuration)
converter.register_unstructure_hook(
    ChannelConfiguration, unstructure_channel_configuration
)
