Readme
======

Installation
------------

The following python package must be installed from PyPI: `caqtus-devices-thorlabs-ell14`.

Usage
-----

The package provides the `caqtus_devices.motorized_stages.thorlabs_ell14.extension` that
can be registered with the [`caqtus.extension.Experiment.register_device_extension`](https://caqtus.readthedocs.io/en/latest/_autosummary/caqtus.extension.Experiment.html#caqtus.extension.Experiment.register_device_extension)
method.

```python
from caqtus.extension import Experiment
from caqtus_devices.motorized_stages import thorlabs_ell14

my_experiment = Experiment(...)
my_experiment.register_device_extension(thorlabs_ell14.extension)
```