from caqtus.extension import DeviceExtension

from ._compiler import OrcaQuestCompiler
from .configuration import OrcaQuestCameraConfiguration
from .configuration_editor import OrcaQuestConfigurationEditor

orca_quest_extension = DeviceExtension(
    label="Orca Quest camera",
    configuration_type=OrcaQuestCameraConfiguration,
    configuration_factory=OrcaQuestCameraConfiguration.default,
    configuration_dumper=OrcaQuestCameraConfiguration.dump,
    configuration_loader=OrcaQuestCameraConfiguration.load,
    editor_type=OrcaQuestConfigurationEditor,
    compiler_type=OrcaQuestCompiler,
)
