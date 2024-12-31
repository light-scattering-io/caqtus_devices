from caqtus.device.sequencer import SequencerController, SequencerProxy
from caqtus.extension import DeviceExtension

from ._compiler import SpincoreSequencerCompiler
from .configuration import SpincoreSequencerConfiguration
from .configuration_editor import SpincorePulseBlasterDeviceConfigEditor
from .runtime import SpincorePulseBlaster

extension = DeviceExtension(
    label="SpinCore PulseBlaster",
    device_type=SpincorePulseBlaster,
    configuration_type=SpincoreSequencerConfiguration,
    configuration_factory=SpincoreSequencerConfiguration.default,
    configuration_dumper=SpincoreSequencerConfiguration.dump,
    configuration_loader=SpincoreSequencerConfiguration.load,
    editor_type=SpincorePulseBlasterDeviceConfigEditor,
    compiler_type=SpincoreSequencerCompiler,
    controller_type=SequencerController,
    proxy_type=SequencerProxy,
)

__all__ = ["extension"]
