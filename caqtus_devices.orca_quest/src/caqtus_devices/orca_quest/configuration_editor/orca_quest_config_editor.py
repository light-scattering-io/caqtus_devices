from caqtus.gui.condetrol.device_configuration_editors._autogen import (
    build_device_configuration_editor,
)
from ..configuration import OrcaQuestCameraConfiguration

OrcaQuestConfigurationEditor = build_device_configuration_editor(
    OrcaQuestCameraConfiguration
)
