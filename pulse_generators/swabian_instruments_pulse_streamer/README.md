Readme
======

Installation
------------

The following python package must be installed from PyPI: `caqtus-devices-swabian-instruments-pulse-streamer`.

Usage
-----

The package provides the `caqtus_devices.pulse_generators.swabian_instruments_pulse_streamer.extension` that
can be registered with the 
[`caqtus.extension.Experiment.register_device_extension`](https://caqtus.readthedocs.io/en/latest/_autosummary/caqtus.extension.Experiment.html#caqtus.extension.Experiment.register_device_extension) 
method.

```python
from caqtus_devices.pulse_generators import swabian_instruments_pulse_streamer

from caqtus.extension import Experiment

my_experiment = Experiment(...)
my_experiment.register_device_extension(swabian_instruments_pulse_streamer.extension)

```