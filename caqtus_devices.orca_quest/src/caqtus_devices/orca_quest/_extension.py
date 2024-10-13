from caqtus.device.camera import CameraController, CameraProxy
from caqtus.extension import DeviceExtension

from ._compiler import OrcaQuestCompiler
from .configuration import OrcaQuestCameraConfiguration
from .configuration_editor import OrcaQuestConfigurationEditor


def create_orca_quest_device(*args, **kwargs):
    # We only do the import when trying to instantiate the device, because it depends
    # on a library that is not available in all systems.

    from .runtime import OrcaQuestCamera

    return OrcaQuestCamera(*args, **kwargs)


orca_quest_extension = DeviceExtension(
    label="Orca Quest camera",
    device_type=create_orca_quest_device,
    configuration_type=OrcaQuestCameraConfiguration,
    configuration_factory=OrcaQuestCameraConfiguration.default,
    configuration_dumper=OrcaQuestCameraConfiguration.dump,
    configuration_loader=OrcaQuestCameraConfiguration.load,
    editor_type=OrcaQuestConfigurationEditor,
    compiler_type=OrcaQuestCompiler,
    controller_type=CameraController,
    proxy_type=CameraProxy,
)
