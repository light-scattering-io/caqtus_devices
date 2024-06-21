import contextlib
import logging
from typing import Self

import pyvisa
import pyvisa.constants
from caqtus.device import Device

logger = logging.getLogger(__name__)


class SiglentSDG6022X(Device):
    """Siglent SDG6022X arbitrary waveform generator.

    Args:
        resource_name: The VISA resource name of the device.
    """

    def __init__(self, resource_name: str):
        super().__init__()
        self._resource_name = resource_name

        self._exit_stack = contextlib.ExitStack()
        self._resource_manager: pyvisa.ResourceManager
        self._instr: pyvisa.resources.Resource

    def __enter__(self) -> Self:
        try:
            self._resource_manager = self._exit_stack.enter_context(
                contextlib.closing(pyvisa.ResourceManager())
            )
            logger.info("Acquired VISA resource manager")
            self._instr = self._exit_stack.enter_context(
                contextlib.closing(
                    self._resource_manager.open_resource(
                        self._resource_name,
                        access_mode=pyvisa.constants.AccessModes.exclusive_lock,
                    )
                )
            )
            logger.info("Connected to %s", self._resource_name)
            device_identification = self._instr.query("*IDN?")
            logger.info("Device identification: %s", device_identification)
        except Exception:
            self._exit_stack.close()
            raise
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._exit_stack.__exit__(exc_type, exc_val, exc_tb)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    with SiglentSDG6022X("TCPIP0::192.168.137.164::inst0::INSTR") as siglent:
        pass
