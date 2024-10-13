from caqtus.device import DeviceName, DeviceParameter
from caqtus.device.camera import CameraCompiler
from caqtus.shot_compilation import SequenceContext

from .configuration import OrcaQuestCameraConfiguration


class OrcaQuestCompiler(CameraCompiler):
    def __init__(self, device_name: DeviceName, sequence_context: SequenceContext):
        super().__init__(device_name, sequence_context)
        configuration = sequence_context.get_device_configuration(device_name)
        if not isinstance(configuration, OrcaQuestCameraConfiguration):
            raise TypeError(
                f"Expected {OrcaQuestCameraConfiguration} for device {device_name}, "
                f"got {type(configuration)}"
            )
        self.configuration = configuration
        self.device_name = device_name

    class InitializationParams(CameraCompiler.CameraInitializationParameters):
        camera_number: int

    def compile_initialization_parameters(self) -> InitializationParams:
        return self.InitializationParams(
            **super().compile_initialization_parameters(),
            camera_number=self.configuration.camera_number,
        )
        # params = super().compile_initialization_parameters()
        # params["camera_number"] = self.configuration.camera_number
        # return params
