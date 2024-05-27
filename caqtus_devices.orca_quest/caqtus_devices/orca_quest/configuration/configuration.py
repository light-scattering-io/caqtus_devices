from __future__ import annotations

from typing import TYPE_CHECKING

import attrs
from caqtus.device.camera import CameraConfiguration
from caqtus.utils import serialization
from caqtus.utils.roi import RectangularROI, Width, Height

if TYPE_CHECKING:
    # We avoid importing the runtime module because it imports the dcam dependency that
    # might not be installed in the current environment.
    # noinspection PyUnresolvedReferences
    from ..runtime import OrcaQuestCamera


@attrs.define
class OrcaQuestCameraConfiguration(CameraConfiguration["OrcaQuestCamera"]):
    """Holds the configuration for an OrcaQuest camera.

    Attributes:
        camera_number: The number of the camera to use.
    """

    camera_number: int = attrs.field(converter=int, on_setattr=attrs.setters.convert)

    @classmethod
    def dump(cls, config: OrcaQuestCameraConfiguration) -> serialization.JSON:
        return serialization.unstructure(config)

    @classmethod
    def load(cls, data: serialization.JSON) -> OrcaQuestCameraConfiguration:
        return serialization.structure(data, OrcaQuestCameraConfiguration)

    @classmethod
    def default(cls) -> OrcaQuestCameraConfiguration:
        return OrcaQuestCameraConfiguration(
            camera_number=0,
            remote_server=None,
            roi=RectangularROI(
                original_image_size=(Width(4096), Height(2304)),
                x=0,
                y=0,
                width=4096,
                height=2304,
            ),
        )
