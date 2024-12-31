Readme
======

Installation
------------

The following python package must be installed from PyPI: `caqtus-devices-ni6738-analog-card`.

In addition, to use this package to program the NI 6738 card, the NI-DAQmx driver must 
be installed and the device must be registered with in the NI MAX software. 

Usage
-----

The package provides the `caqtus_devices.ni6738_analog_card.ni6738_analog_card_extension` that
can be registered with the 
[`caqtus.extension.Experiment.register_device_extension`](https://caqtus.readthedocs.io/en/latest/_autosummary/caqtus.extension.Experiment.html#caqtus.extension.Experiment.register_device_extension) 
method.

```python
from caqtus_devices.ni6738_analog_card import ni6738_analog_card_extension

from caqtus.extension import Experiment

my_experiment = Experiment(...)
my_experiment.register_device_extension(ni6738_analog_card_extension)

```