from caqtus.gui.autogen import generate_device_configuration_editor, AttributeOverride

from ..configuration import OrcaQuestCameraConfiguration

OrcaQuestConfigurationEditor = generate_device_configuration_editor(
    OrcaQuestCameraConfiguration, roi=AttributeOverride(order=1)
)
