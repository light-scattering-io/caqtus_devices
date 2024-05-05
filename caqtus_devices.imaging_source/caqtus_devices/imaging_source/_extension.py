from caqtus.extension import DeviceExtension

from .configuration import ImagingSourceCameraConfiguration
from .configuration_editor import ImagingSourceCameraConfigurationEditor

imaging_source_extension = DeviceExtension(
    label="Imaging Source camera",
    configuration_type=ImagingSourceCameraConfiguration,
    configuration_factory=ImagingSourceCameraConfiguration.default,
    editor_type=ImagingSourceCameraConfigurationEditor,
)
