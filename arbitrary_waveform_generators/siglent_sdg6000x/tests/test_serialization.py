from typing import Optional

from caqtus.device.output_transform import EvaluableOutput
from caqtus.types.expression import Expression
from caqtus_devices.arbitrary_waveform_generators.siglent_sdg6000x import (
    SiglentSDG6022XConfiguration,
)
from caqtus_devices.arbitrary_waveform_generators.siglent_sdg6000x._configuration import (
    ChannelConfiguration,
    SineWaveOutput,
    _converter,
    structure_channel_configuration,
    FSKModulation,
    Modulation,
)


def test_0():
    configuration = SiglentSDG6022XConfiguration(
        remote_server=None,
        resource_name="whatever",
        channels=(SineWaveOutput.default(), "ignore"),
    )

    unstructured = configuration.dump()

    restructured = SiglentSDG6022XConfiguration.load(unstructured)

    assert restructured == configuration

def test_can_load_old_channel_configuration():
    # The '_type' key was not initially present when using only sine wave outputs,
    # so we need to check that we can still load the old format.
    data = {
        "amplitude": "5 V",
        "frequency": "122.8 MHz + probe.frequency/2",
        "load": "High Z",
        "offset": "0 V",
        "output_enabled": True,
    }
    assert structure_channel_configuration(data, ChannelConfiguration) == SineWaveOutput(
        amplitude=Expression("5 V"),
        frequency=Expression("122.8 MHz + probe.frequency/2"),
        load="High Z",
        offset=Expression("0 V"),
        output_enabled=True,
    )


def test_1():
    data = {
        "_type": "SineWaveOutput",
        "amplitude": "1 V",
        "frequency": "1 kHz",
        "load": 50.0,
        "offset": "0 V",
        "output_enabled": True,
    }

    assert (
        structure_channel_configuration(data, ChannelConfiguration)
        == SineWaveOutput.default()
    )


def test_2():
    data = "ignore"

    assert _converter.structure(data, ChannelConfiguration) == "ignore"


def test_3():
    expr = Expression("1 kHz")

    unstructured = _converter.unstructure(expr, EvaluableOutput)

    structured = _converter.structure(unstructured, EvaluableOutput)

    assert structured == expr


def test_4():
    modulation = FSKModulation(hop_frequency=Expression("80 MHz"))

    unstructured = _converter.unstructure(modulation, Optional[Modulation])
    assert unstructured["modulation_type"] == "FSKModulation"
    structured = _converter.structure(unstructured, Optional[Modulation])

    assert structured == modulation


def test_6():
    sine_config = SineWaveOutput.default()
    sine_config.modulation = FSKModulation(hop_frequency=Expression("80 MHz"))

    unstructured = _converter.unstructure(sine_config, SineWaveOutput)

    structured = _converter.structure(unstructured, SineWaveOutput)

    assert structured == sine_config


def test_5():
    config = SiglentSDG6022XConfiguration.default()

    config.channels = (SineWaveOutput.default(), "ignore")
    config.channels[0].modulation = FSKModulation(hop_frequency=Expression("80 MHz"))

    unstructured = config.dump()
    structured = SiglentSDG6022XConfiguration.load(unstructured)

    assert structured == config
