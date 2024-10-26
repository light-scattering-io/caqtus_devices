from caqtus.gui.condetrol.device_configuration_editors._autogen import (
    build_device_configuration_editor,
    get_editor_builder,
)

from ..configuration import OrcaQuestCameraConfiguration


config_editor_type = build_device_configuration_editor(
    OrcaQuestCameraConfiguration, get_editor_builder()
)
