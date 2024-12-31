Readme
======

Installation
------------

The following python package must be installed from PyPI: `caqtus_devices.imaging_source`.

In addition, to use this package to talk to a camera, the library tisgrabber must be 
installed.
The library can be downloaded from the Imaging Source website.
In the [download page](https://www.theimagingsource.com/en-us/support/download/),
section SDK, install the IC Imaging Control C Library if you are using Windows.
Untested on other platforms.

Usage
-----

The package provides the `caqtus_devices.imaging_source.imaging_source_extension` that
can be registered with the 
[`caqtus.extension.Experiment.register_device_extension`](https://caqtus.readthedocs.io/en/latest/_autosummary/caqtus.extension.Experiment.html#caqtus.extension.Experiment.register_device_extension) 
method.

```python
from caqtus.extension import Experiment
from caqtus_devices.imaging_source import imaging_source_extension

my_experiment = Experiment(...)
my_experiment.register_device_extension(imaging_source_extension)
```