from caqtus.extension import DeviceExtension

from ._compiler import SiglentSDG6022XCompiler
from ._configuration import SiglentSDG6022XConfiguration
from ._controller import SiglentSDG6022XController
from ._editor import SiglentSDG6022XConfigEditor
from ._proxy import SiglentSDG6022XProxy
from ._runtime import SiglentSDG6022X

extension = DeviceExtension(
    label="Siglent SDG6000X AWG",
    device_type=SiglentSDG6022X,
    configuration_type=SiglentSDG6022XConfiguration,
    configuration_dumper=SiglentSDG6022XConfiguration.dump,
    configuration_loader=SiglentSDG6022XConfiguration.load,
    configuration_factory=SiglentSDG6022XConfiguration.default,
    compiler_type=SiglentSDG6022XCompiler,
    proxy_type=SiglentSDG6022XProxy,
    controller_type=SiglentSDG6022XController,
    editor_type=SiglentSDG6022XConfigEditor,
)
