import typing
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QSizePolicy, QPushButton, QLabel
)
from PyQt6 import QtCore

class VectorDefined(QWidget):
    def __init__(self, vector_data: typing.List[int], parent: typing.Optional['QWidget'] = ...) -> None:
        super().__init__(parent)
        self.vector_data = vector_data
        self.setup_ui()

    def setup_ui(self):
        self.horizontal_layout = QHBoxLayout(self)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.pushButton = QPushButton(self)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.horizontal_layout.addWidget(self.pushButton)
        self.label = QLabel(self)
        self.label.setText(f"({', '.join(str(a) for a in self.vector_data)})")
        self.horizontal_layout.addWidget(self.label)
        
        self.retranslate_ui()

    def retranslate_ui(self):
        _translate = QtCore.QCoreApplication.translate
        self.pushButton.setText(_translate("MainWindow", "Remove"))