from typing import Mapping, Any

from caqtus.device import DeviceName, DeviceParameter
from caqtus.shot_compilation import DeviceCompiler, SequenceContext, ShotContext
from caqtus.types.units import Quantity
from .configuration import ElliptecELL14RotationStageConfiguration


class ElliptecELL14RotationStageCompiler(DeviceCompiler):
    def __init__(self, device_name: DeviceName, sequence_context: SequenceContext):
        super().__init__(device_name, sequence_context)
        self.device_name = device_name
        configuration = sequence_context.get_device_configuration(device_name)
        if not isinstance(configuration, ElliptecELL14RotationStageConfiguration):
            raise TypeError(
                f"Expected ElliptecELL14RotationStageConfiguration, got "
                f"{type(configuration)}"
            )
        self.configuration = configuration

    def compile_initialization_parameters(self) -> Mapping[DeviceParameter, Any]:
        return {
            **super().compile_initialization_parameters(),
            DeviceParameter("name"): self.device_name,
            DeviceParameter("serial_port"): self.configuration.serial_port,
            DeviceParameter("device_id"): self.configuration.device_id,
        }

    def compile_shot_parameters(self, shot_context: ShotContext) -> Mapping[str, Any]:
        position = self.configuration.position
        value = position.evaluate(shot_context.get_variables())
        if not isinstance(value, Quantity):
            raise TypeError(f"Expected position to be a Quantity, got {type(value)}")
        angle_in_degrees = value.to("degree").magnitude
        return {"position": angle_in_degrees}
