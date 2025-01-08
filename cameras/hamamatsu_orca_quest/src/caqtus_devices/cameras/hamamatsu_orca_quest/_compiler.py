from caqtus.device import DeviceName
from caqtus.device.camera import CameraCompiler
from caqtus.shot_compilation import SequenceContext

from .configuration import OrcaQuestCameraConfiguration
from .configuration.configuration import SensorMode, ReadoutSpeed


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
        sensor_mode: SensorMode
        readout_speed: ReadoutSpeed

    def compile_initialization_parameters(self) -> InitializationParams:
        return self.InitializationParams(
            **super().compile_initialization_parameters(),
            camera_number=self.configuration.camera_number,
            sensor_mode=self.configuration.sensor_mode,
            readout_speed=self.configuration.readout_speed,
        )
