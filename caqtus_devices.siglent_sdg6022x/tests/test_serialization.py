from caqtus_devices.siglent_sdg6022x import SiglentSDG6022XConfiguration
from caqtus_devices.siglent_sdg6022x._configuration import (
    converter,
    ChannelConfiguration,
    SineWaveOutput,
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


def test_1():
    data = {
        "_type": "SineWaveOutput",
        "amplitude": "1 V",
        "frequency": "1 kHz",
        "load": 50.0,
        "offset": "0 V",
        "output_enabled": True,
    }

    assert converter.structure(data, ChannelConfiguration) == SineWaveOutput.default()


def test_2():
    data = "ignore"

    assert converter.structure(data, ChannelConfiguration) == "ignore"
