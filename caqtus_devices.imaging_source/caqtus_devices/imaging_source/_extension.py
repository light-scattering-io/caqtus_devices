from caqtus.extension import DeviceExtension

from .configuration import ImagingSourceCameraConfiguration
from .configuration_editor import ImagingSourceCameraConfigurationEditor

imaging_source_extension = DeviceExtension(
    label="Imaging Source camera",
    configuration_type=ImagingSourceCameraConfiguration,
    configuration_factory=ImagingSourceCameraConfiguration.default,
    configuration_dumper=ImagingSourceCameraConfiguration.dump,
    configuration_loader=ImagingSourceCameraConfiguration.load,
    editor_type=ImagingSourceCameraConfigurationEditor,
)
