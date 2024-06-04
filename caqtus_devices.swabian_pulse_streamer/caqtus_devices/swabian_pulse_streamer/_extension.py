from caqtus.device.sequencer import SequencerController, SequencerProxy
from caqtus.extension import DeviceExtension

from ._compiler import SwabianPulseStreamerCompiler
from .configuration import SwabianPulseStreamerConfiguration
from .configuration_editor import SwabianPulseStreamerDeviceConfigEditor

swabian_pulse_streamer_extension = DeviceExtension(
    label="Swabian Pulse Streamer",
    configuration_type=SwabianPulseStreamerConfiguration,
    configuration_factory=SwabianPulseStreamerConfiguration.default,
    configuration_dumper=SwabianPulseStreamerConfiguration.dump,
    configuration_loader=SwabianPulseStreamerConfiguration.load,
    editor_type=SwabianPulseStreamerDeviceConfigEditor,
    compiler_type=SwabianPulseStreamerCompiler,
    controller_type=SequencerController,
    proxy_type=SequencerProxy,
)
