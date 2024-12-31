# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sine_editor.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFormLayout,
    QLabel, QLineEdit, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_SineEditor(object):
    def setupUi(self, SineEditor):
        if not SineEditor.objectName():
            SineEditor.setObjectName(u"SineEditor")
        SineEditor.resize(400, 300)
        self.verticalLayout = QVBoxLayout(SineEditor)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.enabledLabel = QLabel(SineEditor)
        self.enabledLabel.setObjectName(u"enabledLabel")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.enabledLabel)

        self.enabledCheckBox = QCheckBox(SineEditor)
        self.enabledCheckBox.setObjectName(u"enabledCheckBox")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.enabledCheckBox)

        self.loadLabel = QLabel(SineEditor)
        self.loadLabel.setObjectName(u"loadLabel")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.loadLabel)

        self.loadComboBox = QComboBox(SineEditor)
        self.loadComboBox.setObjectName(u"loadComboBox")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.loadComboBox)

        self.frequencyLabel = QLabel(SineEditor)
        self.frequencyLabel.setObjectName(u"frequencyLabel")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.frequencyLabel)

        self.frequencyLineEdit = QLineEdit(SineEditor)
        self.frequencyLineEdit.setObjectName(u"frequencyLineEdit")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.frequencyLineEdit)

        self.amplitudeLabel = QLabel(SineEditor)
        self.amplitudeLabel.setObjectName(u"amplitudeLabel")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.amplitudeLabel)

        self.amplitudeLineEdit = QLineEdit(SineEditor)
        self.amplitudeLineEdit.setObjectName(u"amplitudeLineEdit")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.amplitudeLineEdit)

        self.offsetLabel = QLabel(SineEditor)
        self.offsetLabel.setObjectName(u"offsetLabel")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.offsetLabel)

        self.offsetLineEdit = QLineEdit(SineEditor)
        self.offsetLineEdit.setObjectName(u"offsetLineEdit")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.offsetLineEdit)


        self.verticalLayout.addLayout(self.formLayout)


        self.retranslateUi(SineEditor)

        QMetaObject.connectSlotsByName(SineEditor)
    # setupUi

    def retranslateUi(self, SineEditor):
        SineEditor.setWindowTitle(QCoreApplication.translate("SineEditor", u"Form", None))
        self.enabledLabel.setText(QCoreApplication.translate("SineEditor", u"Enabled", None))
        self.loadLabel.setText(QCoreApplication.translate("SineEditor", u"Load", None))
        self.frequencyLabel.setText(QCoreApplication.translate("SineEditor", u"Frequency", None))
        self.amplitudeLabel.setText(QCoreApplication.translate("SineEditor", u"Amplitude", None))
        self.offsetLabel.setText(QCoreApplication.translate("SineEditor", u"Offset", None))
    # retranslateUi

