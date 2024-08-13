from caqtus.device import DeviceController

from ._proxy import SiglentSDG6022XProxy
from ._runtime import SiglentState


class SiglentSDG6022XController(DeviceController):
    # noinspection PyMethodOverriding
    async def run_shot(
        self, siglent: SiglentSDG6022XProxy, /, state: SiglentState
    ) -> None:
        await siglent.update_state(state)
        await self.wait_all_devices_ready()
