from caqtus.device.remote import DeviceProxy

from ._runtime import SiglentSDG6022X, SiglentState


class SiglentSDG6022XProxy(DeviceProxy[SiglentSDG6022X]):
    async def update_state(self, state: SiglentState) -> None:
        await self.call_method("update_state", state)
