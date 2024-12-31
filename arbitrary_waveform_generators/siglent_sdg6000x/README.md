Readme
======

Installation
------------

The following python package must be installed from PyPI: `caqtus-devices-siglent-sdg6000x`.

This package depends on pyvisa, which requires a backend to communicate with the device.
Follow the instructions in the pyvisa documentation to install the backend of your choice.

You might also need to add the resource for example in NI MAX.

Usage
-----

The package provides the `caqtus_devices.arbitrary_waveform_generators.siglent_sdg6000x` that
can be registered with the 
[`caqtus.extension.Experiment.register_device_extension`](https://caqtus.readthedocs.io/en/latest/_autosummary/caqtus.extension.Experiment.html#caqtus.extension.Experiment.register_device_extension) 
method.

```python
from caqtus.extension import Experiment
from caqtus_devices.arbitrary_waveform_generators.siglent_sdg6000x import extension

my_experiment = Experiment(...)
my_experiment.register_device_extension(extension)
```