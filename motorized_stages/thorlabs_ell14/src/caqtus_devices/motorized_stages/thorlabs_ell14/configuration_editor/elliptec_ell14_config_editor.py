from caqtus.gui.autogen import build_device_configuration_editor

from ..configuration import ElliptecELL14RotationStageConfiguration

ElliptecELL14RotationStageConfigEditor = build_device_configuration_editor(
    ElliptecELL14RotationStageConfiguration
)
