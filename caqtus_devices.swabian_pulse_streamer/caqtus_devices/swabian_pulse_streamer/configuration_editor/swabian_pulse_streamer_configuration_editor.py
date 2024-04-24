from typing import Optional

from PySide6.QtWidgets import QLineEdit, QWidget
from caqtus.gui.condetrol.device_configuration_editors import (
    SequencerConfigurationEditor,
)

from ..configuration import SwabianPulseStreamerConfiguration


class SwabianPulseStreamerDeviceConfigEditor(
    SequencerConfigurationEditor[SwabianPulseStreamerConfiguration]
):
    def __init__(self, config: SwabianPulseStreamerConfiguration,
                 parent: Optional[QWidget] = None):
        super().__init__(config, parent)

        self.time_step_spinbox.setRange(1, 1)

        self._ip_address = QLineEdit(self)
        self._ip_address.setText(config.ip_address)
        self.form.insertRow(1, "Ip address", self._ip_address)

    def get_configuration(self) -> SwabianPulseStreamerConfiguration:
        config = super().get_configuration()
        config.ip_address = self._ip_address.text()
        return config
