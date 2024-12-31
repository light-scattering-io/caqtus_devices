from caqtus.device.camera import CameraController, CameraProxy
from caqtus.extension import DeviceExtension

from ._compiler import ImagingSourceCameraCompiler
from .configuration import ImagingSourceCameraConfiguration
from .configuration_editor import ImagingSourceCameraConfigurationEditor


def create_new_imaging_source_camera(*args, **kwargs):
    from .runtime import ImagingSourceCameraDMK33GR0134

    return ImagingSourceCameraDMK33GR0134(*args, **kwargs)


extension = DeviceExtension(
    label="Imaging Source camera",
    device_type=create_new_imaging_source_camera,
    configuration_type=ImagingSourceCameraConfiguration,
    configuration_factory=ImagingSourceCameraConfiguration.default,
    configuration_dumper=ImagingSourceCameraConfiguration.dump,
    configuration_loader=ImagingSourceCameraConfiguration.load,
    editor_type=ImagingSourceCameraConfigurationEditor,
    compiler_type=ImagingSourceCameraCompiler,
    controller_type=CameraController,
    proxy_type=CameraProxy,
)
