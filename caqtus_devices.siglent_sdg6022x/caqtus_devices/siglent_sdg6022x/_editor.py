from caqtus.gui.condetrol.device_configuration_editors import (
    FormDeviceConfigurationEditor,
)

from ._configuration import SiglentSDG6022XConfiguration


class SiglentSDG6022XConfigEditor(FormDeviceConfigurationEditor):
    def __init__(self, device_configuration: SiglentSDG6022XConfiguration, parent=None):
        super().__init__(device_configuration, parent)
