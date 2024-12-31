from caqtus.device import DeviceName
from caqtus.device.sequencer import SequencerCompiler
from caqtus.shot_compilation import SequenceContext

from .configuration import SwabianPulseStreamerConfiguration


class SwabianPulseStreamerCompiler(SequencerCompiler):
    def __init__(self, device_name: DeviceName, sequence_context: SequenceContext):
        super().__init__(device_name, sequence_context)
        configuration = sequence_context.get_device_configuration(device_name)
        if not isinstance(configuration, SwabianPulseStreamerConfiguration):
            raise TypeError(
                f"Expected {SwabianPulseStreamerConfiguration} for device "
                f"{device_name}, got {type(configuration)}"
            )
        self.configuration = configuration
        self.device_name = device_name

    def compile_initialization_parameters(self):
        return {
            **super().compile_initialization_parameters(),
            "name": self.device_name,
            "ip_address": self.configuration.ip_address,
        }
