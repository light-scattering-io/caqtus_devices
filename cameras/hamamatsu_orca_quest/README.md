Readme
======

Installation
------------

The following python package must be installed from PyPI: `caqtus-devices-hamamatsu-orca-quest`.

In addition, to use this package to communicate with the camera, the Hamamatsu DCAM-API 
must be installed.
Usage
-----

The package provides the `caqtus_devices.cameras.hamamatsu_orca_quest.extension` that
can be registered with the 
[`caqtus.extension.Experiment.register_device_extension`](https://caqtus.readthedocs.io/en/latest/_autosummary/caqtus.extension.Experiment.html#caqtus.extension.Experiment.register_device_extension) 
method.

```python
from caqtus_devices.cameras import hamamatsu_orca_quest

from caqtus.extension import Experiment

my_experiment = Experiment(...)
my_experiment.register_device_extension(hamamatsu_orca_quest.extension)

```