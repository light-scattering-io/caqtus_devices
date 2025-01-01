from caqtus.device import DeviceController

from ._proxy import ElliptecELL14RotationStageProxy


class ElliptecELL14RotationStageController(DeviceController):
    # noinspection PyMethodOverriding
    async def run_shot(
        self,
        device: ElliptecELL14RotationStageProxy,
        /,
        position: float,
    ) -> None:
        await device.update_parameters(position=position)
        await self.wait_all_devices_ready()
