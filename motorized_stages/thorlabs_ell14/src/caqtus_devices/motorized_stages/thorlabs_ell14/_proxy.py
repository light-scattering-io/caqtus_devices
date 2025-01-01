from caqtus.device.remote import DeviceProxy
from .runtime import ElliptecELL14RotationStage


class ElliptecELL14RotationStageProxy(DeviceProxy[ElliptecELL14RotationStage]):
    async def update_parameters(self, position: float) -> None:
        return await self.call_method("update_parameters", position=position)
