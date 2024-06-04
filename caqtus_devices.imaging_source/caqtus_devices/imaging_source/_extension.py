from caqtus.device.camera import CameraController, CameraProxy
from caqtus.extension import DeviceExtension

from ._compiler import ImagingSourceCameraCompiler
from .configuration import ImagingSourceCameraConfiguration
from .configuration_editor import ImagingSourceCameraConfigurationEditor

imaging_source_extension = DeviceExtension(
    label="Imaging Source camera",
    configuration_type=ImagingSourceCameraConfiguration,
    configuration_factory=ImagingSourceCameraConfiguration.default,
    configuration_dumper=ImagingSourceCameraConfiguration.dump,
    configuration_loader=ImagingSourceCameraConfiguration.load,
    editor_type=ImagingSourceCameraConfigurationEditor,
    compiler_type=ImagingSourceCameraCompiler,
    controller_type=CameraController,
    proxy_type=CameraProxy,
)
