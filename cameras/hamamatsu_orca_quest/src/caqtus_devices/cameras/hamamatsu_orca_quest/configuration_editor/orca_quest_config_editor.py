from caqtus.gui.autogen import build_device_configuration_editor, AttributeOverride
from ..configuration import OrcaQuestCameraConfiguration

OrcaQuestConfigurationEditor = build_device_configuration_editor(
    OrcaQuestCameraConfiguration, roi=AttributeOverride(order=1)
)
