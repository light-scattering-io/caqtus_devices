from caqtus.device.sequencer import SequencerController, SequencerProxy
from caqtus.extension import DeviceExtension

from ._compiler import NI6738SequencerCompiler
from .configuration import NI6738SequencerConfiguration
from .configuration_editor import NI6738DeviceConfigEditor
from .runtime import NI6738AnalogCard

extension = DeviceExtension(
    label="NI 6738 analog card",
    device_type=NI6738AnalogCard,
    configuration_type=NI6738SequencerConfiguration,
    configuration_factory=NI6738SequencerConfiguration.default,
    configuration_dumper=NI6738SequencerConfiguration.dump,
    configuration_loader=NI6738SequencerConfiguration.load,
    editor_type=NI6738DeviceConfigEditor,
    compiler_type=NI6738SequencerCompiler,
    controller_type=SequencerController,
    proxy_type=SequencerProxy,
)
