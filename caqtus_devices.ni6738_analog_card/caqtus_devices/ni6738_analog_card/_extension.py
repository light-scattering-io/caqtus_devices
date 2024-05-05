from caqtus.extension import DeviceExtension
from .configuration import NI6738SequencerConfiguration
from .configuration_editor import NI6738DeviceConfigEditor

ni6738_analog_card_extension = DeviceExtension(
    label="NI 6738 analog card",
    configuration_type=NI6738SequencerConfiguration,
    configuration_factory=NI6738SequencerConfiguration.default,
    editor_type=NI6738DeviceConfigEditor,
)
