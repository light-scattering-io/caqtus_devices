from __future__ import annotations

from typing import Literal, TYPE_CHECKING

import attrs

from caqtus.device.camera import CameraConfiguration
from caqtus.types.image import Width, Height
from caqtus.types.image.roi import RectangularROI
from caqtus.utils import serialization

if TYPE_CHECKING:
    from ..runtime import ImagingSourceCameraDMK33GR0134  # noqa: F401


@attrs.define
class ImagingSourceCameraConfiguration(
    CameraConfiguration["ImagingSourceCameraDMK33GR0134"]
):
    """Holds the configuration for a camera from The Imaging Source.

    Attributes:
        camera_name: The name of the camera to use.
            This is written on the camera.
        format: The format of the camera.
            Can be "Y16" or "Y800" respectively for 16-bit and 8-bit monochrome images.
    """

    camera_name: str = attrs.field(converter=str, on_setattr=attrs.setters.convert)
    format: Literal["Y16", "Y800"] = attrs.field(
        validator=attrs.validators.in_(["Y16", "Y800"]),
        on_setattr=attrs.setters.validate,
    )

    @classmethod
    def default(cls) -> ImagingSourceCameraConfiguration:
        width = Width(1280)
        height = Height(960)
        return cls(
            camera_name="DMK33GR0134",
            format="Y16",
            remote_server=None,
            roi=RectangularROI(
                width=width,
                height=height,
                x=0,
                y=0,
                original_image_size=(width, height),
            ),
        )

    @classmethod
    def dump(cls, config: ImagingSourceCameraConfiguration) -> serialization.JSON:
        return serialization.unstructure(config)

    @classmethod
    def load(cls, data: serialization.JSON) -> ImagingSourceCameraConfiguration:
        return serialization.structure(data, ImagingSourceCameraConfiguration)
