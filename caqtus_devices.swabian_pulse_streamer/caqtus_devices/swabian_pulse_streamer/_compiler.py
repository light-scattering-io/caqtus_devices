from caqtus.device import DeviceName, DeviceParameter
from caqtus.device.sequencer import SequencerCompiler
from caqtus.shot_compilation import SequenceContext

from .configuration import SwabianPulseStreamerConfiguration


class SwabianPulseStreamerCompiler(SequencerCompiler):
    def __init__(self, device_name: DeviceName, sequence_context: SequenceContext):
        super().__init__(device_name, sequence_context)
        configuration = sequence_context.get_device_configuration(device_name)
        if not isinstance(configuration, SwabianPulseStreamerConfiguration):
            raise TypeError(
                f"Expected {SwabianPulseStreamerConfiguration} for device {device_name}, "
                f"got {type(configuration)}"
            )
        self.configuration = configuration
        self.device_name = device_name

    def compile_initialization_parameters(self):
        return {
            **super().compile_initialization_parameters(),
            DeviceParameter("name"): self.device_name,
            DeviceParameter("ip_address"): self.configuration.ip_address,
        }
