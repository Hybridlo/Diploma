import typing
from functools import partial
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QSizePolicy, QLineEdit
)
from PyQt6 import QtCore, QtGui

class VectorDefiner(QWidget):
    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.line_edits: typing.List[QLineEdit] = []
        self.setup_ui()

    def process_line_edit_finished(self) -> None:
        if self.line_edits[-1].text():
            if len(self.line_edits) > 1:
                self.line_edits[-2].setDisabled(True)

            self.new_line_edit()

        elif len(self.line_edits) > 1 and not self.line_edits[-2].text():
            removing = self.line_edits.pop()
            removing.deleteLater()

            if len(self.line_edits) > 1:
                self.line_edits[-2].setDisabled(False)

    def new_line_edit(self) -> None:
        line_edit = QLineEdit(self)
        self.line_edits.append(line_edit)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(line_edit.sizePolicy().hasHeightForWidth())
        line_edit.setSizePolicy(sizePolicy)
        line_edit.setMaximumSize(QtCore.QSize(60, 16777215))
        line_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression("[0-9]*")))
        line_edit.editingFinished.connect(self.process_line_edit_finished)
        self.horizontal_layout.addWidget(line_edit)

    def setup_ui(self) -> None:
        self.horizontal_layout = QHBoxLayout(self)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.new_line_edit()