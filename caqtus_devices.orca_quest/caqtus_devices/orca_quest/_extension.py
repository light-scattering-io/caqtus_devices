from caqtus.extension import DeviceExtension
from .configuration import OrcaQuestCameraConfiguration
from .configuration_editor import OrcaQuestConfigurationEditor

orca_quest_extension = DeviceExtension(
    label="Orca Quest camera",
    configuration_type=OrcaQuestCameraConfiguration,
    configuration_factory=OrcaQuestCameraConfiguration.default,
    editor_type=OrcaQuestConfigurationEditor,
)
