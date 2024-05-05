from caqtus.extension import DeviceExtension

from ..configuration import SpincoreSequencerConfiguration
from ..configuration_editor import SpincorePulseBlasterDeviceConfigEditor

spincore_pulse_blaster_extension = DeviceExtension(
    label="SpinCore PulseBlaster",
    configuration_type=SpincoreSequencerConfiguration,
    configuration_factory=SpincoreSequencerConfiguration.default,
    configuration_dumper=SpincoreSequencerConfiguration.dump,
    configuration_loader=SpincoreSequencerConfiguration.load,
    editor_type=SpincorePulseBlasterDeviceConfigEditor,
)

__all__ = ["spincore_pulse_blaster_extension"]
