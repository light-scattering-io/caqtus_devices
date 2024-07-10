from typing import Optional, assert_never

from PySide6.QtWidgets import (
    QLineEdit,
    QWidget,
    QTabWidget,
    QVBoxLayout,
    QButtonGroup,
    QRadioButton,
    QGroupBox,
)
from caqtus.gui.condetrol.device_configuration_editors import (
    FormDeviceConfigurationEditor,
)
from caqtus.types.expression import Expression

from ._configuration import (
    SiglentSDG6022XConfiguration,
    ChannelConfiguration,
    SineWaveOutput,
)
from .sine_editor_ui import Ui_SineEditor


class SiglentSDG6022XConfigEditor(FormDeviceConfigurationEditor):
    def __init__(self, device_configuration: SiglentSDG6022XConfiguration, parent=None):
        super().__init__(device_configuration, parent)

        self.resource_name = QLineEdit(device_configuration.resource_name, self)
        self.resource_name.setPlaceholderText("Enter the VISA resource name")
        self.form.addRow("Resource Name", self.resource_name)

        self.channels = QTabWidget(self)
        self.channels.addTab(
            ChannelConfigEditor(device_configuration.channels[0]), "Channel 1"
        )
        self.channels.addTab(
            ChannelConfigEditor(device_configuration.channels[1]), "Channel 2"
        )
        self.form.addRow("Channels", self.channels)

    def get_configuration(self) -> SiglentSDG6022XConfiguration:
        config = super().get_configuration()
        config.resource_name = self.resource_name.text()
        # noinspection PyUnresolvedReferences
        config.channels = (
            self.channels.widget(0).read_config(),
            self.channels.widget(1).read_config(),
        )
        return config


class ChannelConfigEditor(QWidget):
    def __init__(
        self, channel_config: ChannelConfiguration, parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        group_box = QGroupBox("Output", self)
        group_box_layout = QVBoxLayout(group_box)
        group_box.setLayout(group_box_layout)
        layout.addWidget(group_box)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)

        self.ignore_button = QRadioButton("Ignore", self)
        self.button_group.addButton(self.ignore_button)
        group_box_layout.addWidget(self.ignore_button)

        self.sine_wave_button = QRadioButton("Sine", self)
        self.button_group.addButton(self.sine_wave_button)
        group_box_layout.addWidget(self.sine_wave_button)

        self.sine_editor = SineWaveOutputEditor()
        layout.addWidget(self.sine_editor)

        self.sine_wave_button.toggled.connect(self.sine_editor.setVisible)
        self.apply(channel_config)

        layout.addStretch(1)

    def apply(self, config: ChannelConfiguration):
        if config == "ignore":
            self.ignore_button.setChecked(True)
        else:
            self.sine_wave_button.setChecked(True)
            self.sine_editor.apply(config)
        self.sine_editor.setVisible(self.sine_wave_button.isChecked())

    def read_config(self) -> ChannelConfiguration:
        if self.ignore_button.isChecked():
            return "ignore"
        elif self.sine_wave_button.isChecked():
            return self.sine_editor.read_config()
        assert False, "No button is checked"


class SineWaveOutputEditor(QWidget, Ui_SineEditor):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setupUi(self)
        self.loadComboBox.addItems(["50 Ω", "High Z"])

    def apply(self, config: SineWaveOutput):
        self.enabledCheckBox.setChecked(config.output_enabled)
        if config.load == 50.0:
            self.loadComboBox.setCurrentText("50 Ω")
        elif config.load == "High Z":
            self.loadComboBox.setCurrentText("High Z")
        else:
            assert_never(config.load)
        if not isinstance(config.frequency, Expression):
            raise NotImplementedError
        self.frequencyLineEdit.setText(str(config.frequency))
        if not isinstance(config.amplitude, Expression):
            raise NotImplementedError
        self.amplitudeLineEdit.setText(str(config.amplitude))
        if not isinstance(config.offset, Expression):
            raise NotImplementedError
        self.offsetLineEdit.setText(str(config.offset))

    def read_config(self) -> SineWaveOutput:
        return SineWaveOutput(
            output_enabled=self.enabledCheckBox.isChecked(),
            load=50.0 if self.loadComboBox.currentText() == "50 Ω" else "High Z",
            frequency=Expression(self.frequencyLineEdit.text()),
            amplitude=Expression(self.amplitudeLineEdit.text()),
            offset=Expression(self.offsetLineEdit.text()),
        )
