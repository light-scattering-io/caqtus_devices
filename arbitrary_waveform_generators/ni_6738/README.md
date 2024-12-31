Readme
======

Installation
------------

The following python package must be installed from PyPI: `caqtus-devices-ni-6738`.

In addition, to use this package to program the NI 6738 card, the NI-DAQmx driver must 
be installed and the device must be registered with in the NI MAX software. 

Usage
-----

The package provides the `caqtus_devices.arbitrary_waveform_generators.ni_6738.extension` that
can be registered with the 
[`caqtus.extension.Experiment.register_device_extension`](https://caqtus.readthedocs.io/en/latest/_autosummary/caqtus.extension.Experiment.html#caqtus.extension.Experiment.register_device_extension) 
method.

```python
from caqtus_devices.arbitrary_waveform_generators import ni_6738

from caqtus.extension import Experiment

my_experiment = Experiment(...)
my_experiment.register_device_extension(ni_6738.extension)
```