import decimal
from typing import Optional

from PySide6.QtWidgets import QLineEdit

from caqtus.device.sequencer.timing import to_time_step
from caqtus.gui.condetrol.device_configuration_editors.sequencer_configuration_editor import (
    SequencerConfigurationEditor,
)
from ..configuration import NI6738SequencerConfiguration


class NI6738DeviceConfigEditor(
    SequencerConfigurationEditor[NI6738SequencerConfiguration]
):
    def __init__(
        self,
        device_configuration: NI6738SequencerConfiguration,
        parent: Optional[QLineEdit] = None,
    ):
        super().__init__(device_configuration, to_time_step(1), 2500, 100000, parent)

        self._device_id = QLineEdit()
        self.form.insertRow(1, "Device id", self._device_id)
        self._device_id.setText(self.device_configuration.device_id)

    def get_configuration(self) -> NI6738SequencerConfiguration:
        config = super().get_configuration()
        config.device_id = self._device_id.text()
        return config
