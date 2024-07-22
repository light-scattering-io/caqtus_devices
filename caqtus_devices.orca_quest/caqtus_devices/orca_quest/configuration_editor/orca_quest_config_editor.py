from typing import Optional

from PySide6.QtWidgets import QSpinBox, QWidget

from caqtus.gui.condetrol.device_configuration_editors.camera_configuration_editor import (
    CameraConfigurationEditor,
)
from ..configuration import OrcaQuestCameraConfiguration


class OrcaQuestConfigurationEditor(
    CameraConfigurationEditor[OrcaQuestCameraConfiguration]
):
    def __init__(
        self,
        device_config: OrcaQuestCameraConfiguration,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(device_config, parent)

        self._camera_number_spinbox = QSpinBox()
        self._camera_number_spinbox.setRange(0, 99)
        self._camera_number_spinbox.setValue(device_config.camera_number)
        self.insert_row("Camera number", self._camera_number_spinbox, 1)

    def get_configuration(self) -> OrcaQuestCameraConfiguration:
        device_config = super().get_configuration()
        device_config.camera_number = self._camera_number_spinbox.value()
        return device_config
