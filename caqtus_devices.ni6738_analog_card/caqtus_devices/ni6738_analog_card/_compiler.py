from caqtus.device import DeviceName
from caqtus.device.sequencer import SequencerCompiler
from caqtus.shot_compilation import SequenceContext
from .configuration import NI6738SequencerConfiguration


class NI6738SequencerCompiler(SequencerCompiler):
    def __init__(self, device_name: DeviceName, sequence_context: SequenceContext):
        super().__init__(device_name, sequence_context)
        configuration = sequence_context.get_device_configuration(device_name)
        if not isinstance(configuration, NI6738SequencerConfiguration):
            raise TypeError(
                f"Expected a NI6738 configuration for device {device_name}, got "
                f"{type(configuration)}"
            )
        self.configuration = configuration
        self.device_name = device_name

    class InitializationParameters(SequencerCompiler.InitializationParameters):
        name: str
        device_id: str

    def compile_initialization_parameters(self):
        return NI6738SequencerCompiler.InitializationParameters(
            **super().compile_initialization_parameters(),
            name=self.device_name,
            device_id=self.configuration.device_id,
        )
