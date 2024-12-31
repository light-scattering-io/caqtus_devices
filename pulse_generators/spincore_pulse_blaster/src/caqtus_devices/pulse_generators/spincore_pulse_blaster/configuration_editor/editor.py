import decimal
from typing import Optional

from PySide6.QtWidgets import QSpinBox, QWidget

from caqtus.gui.condetrol.device_configuration_editors.sequencer_configuration_editor import (
    SequencerConfigurationEditor,
)
from ..configuration import SpincoreSequencerConfiguration


class SpincorePulseBlasterDeviceConfigEditor(
    SequencerConfigurationEditor[SpincoreSequencerConfiguration]
):
    def __init__(
        self,
        device_configuration: SpincoreSequencerConfiguration,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(
            device_configuration=device_configuration,
            time_step_increment=decimal.Decimal(10),
            smallest_increment_multiple=5,
            parent=parent,
        )

        self._board_number = QSpinBox()
        self._board_number.setRange(0, 100)
        self._board_number.setValue(self.device_configuration.board_number)
        self.form.insertRow(1, "Board number", self._board_number)

    def get_configuration(self) -> SpincoreSequencerConfiguration:
        config = super().get_configuration()
        config.board_number = self._board_number.value()
        return config
