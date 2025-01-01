from caqtus.extension import DeviceExtension

from ._compiler import ElliptecELL14RotationStageCompiler
from ._controller import ElliptecELL14RotationStageController
from ._proxy import ElliptecELL14RotationStageProxy
from .configuration import ElliptecELL14RotationStageConfiguration
from .configuration_editor import ElliptecELL14RotationStageConfigEditor
from .runtime import ElliptecELL14RotationStage

extension = DeviceExtension(
    label="Elliptec ELL14",
    device_type=ElliptecELL14RotationStage,
    configuration_type=ElliptecELL14RotationStageConfiguration,
    configuration_factory=ElliptecELL14RotationStageConfiguration.default,
    configuration_dumper=ElliptecELL14RotationStageConfiguration.dump,
    configuration_loader=ElliptecELL14RotationStageConfiguration.load,
    editor_type=ElliptecELL14RotationStageConfigEditor,
    compiler_type=ElliptecELL14RotationStageCompiler,
    controller_type=ElliptecELL14RotationStageController,
    proxy_type=ElliptecELL14RotationStageProxy,
)
