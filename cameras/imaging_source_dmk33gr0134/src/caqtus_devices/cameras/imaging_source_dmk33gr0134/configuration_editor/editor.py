from caqtus.gui.autogen import build_device_configuration_editor, AttributeOverride
from ..configuration import ImagingSourceCameraConfiguration

ImagingSourceCameraConfigurationEditor = build_device_configuration_editor(
    ImagingSourceCameraConfiguration, roi=AttributeOverride(order=1)
)


# class ImagingSourceCameraConfigurationEditor(
#     CameraConfigurationEditor[ImagingSourceCameraConfiguration]
# ):
#     def __init__(
#         self,
#         configuration: ImagingSourceCameraConfiguration,
#         parent: Optional[QWidget] = None,
#     ):
#         super().__init__(configuration, parent)
#
#         self._camera_name = QLineEdit()
#         self._camera_name.setText(configuration.camera_name)
#         self.insert_row("Camera name", self._camera_name, 1)
#         self._format_combo_box = QComboBox()
#         self._format_combo_box.addItems(["Y800", "Y16"])
#         self._format_combo_box.setCurrentText(configuration.format)
#         self.insert_row("Format", self._format_combo_box, 2)
#
#     def get_configuration(self) -> ImagingSourceCameraConfiguration:
#         configuration = super().get_configuration()
#         configuration.camera_name = self._camera_name.text()
#         format_ = self._format_combo_box.currentText()
#         assert format_ == "Y800" or format_ == "Y16"
#         configuration.format = format_
#         return configuration
