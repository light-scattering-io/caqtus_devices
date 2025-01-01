Readme
======

Installation
------------

The following python package must be installed from PyPI: `{{ cookiecutter.pypi_name }}`.

Usage
-----

The package provides the `{{ cookiecutter.package_name }}.extension` that
can be registered with the [`caqtus.extension.Experiment.register_device_extension`](https://caqtus.readthedocs.io/en/latest/_autosummary/caqtus.extension.Experiment.html#caqtus.extension.Experiment.register_device_extension)
method.

```python
from caqtus.extension import Experiment
from caqtus_devices.{{cookiecutter.device_category_module}} import {{cookiecutter.device_module}}

my_experiment = Experiment(...)
my_experiment.register_device_extension({{cookiecutter.device_module}}.extension)
```