from pytestqt.qtbot import QtBot

from caqtus_devices.siglent_sdg6022x._configuration import SiglentSDG6022XConfiguration
from caqtus_devices.siglent_sdg6022x._editor import SiglentSDG6022XConfigEditor


def test_0(qtbot: QtBot):
    config = SiglentSDG6022XConfiguration.default()
    editor = SiglentSDG6022XConfigEditor(config)

    qtbot.addWidget(editor)
    editor.show()
    assert editor.get_configuration() == config
