from caqtus.gui.autogen import build_device_configuration_editor
from ..configuration import OrcaQuestCameraConfiguration

OrcaQuestConfigurationEditor = build_device_configuration_editor(
    OrcaQuestCameraConfiguration
)
