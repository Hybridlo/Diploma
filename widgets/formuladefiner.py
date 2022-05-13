import typing
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QSizePolicy, QLineEdit, QLabel
)
from PyQt6 import QtCore, QtGui

from utils.const import SUBSCRIPT_NUMBERS

class FormulaDefiner(QWidget):
    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.line_edits: typing.List[QLineEdit] = []
        self.labels: typing.List[QLabel] = []
        self.setup_ui()

    @property
    def formula_size(self) -> int:
        return len(self.line_edits) - 2     # b doesn't get included in the formula

    @property
    def formula_data(self) -> typing.List[int]:
        result: typing.List[int] = []

        for line_edit in self.line_edits:
            num_text = line_edit.text()
            if num_text:
                result.append(int(num_text))

        return result

    def process_line_edit_finished(self) -> None:
        if self.line_edits[-1].text():
            if len(self.line_edits) > 1:
                self.line_edits[-2].setDisabled(True)

            self.new_line_edit_and_label()

        elif len(self.line_edits) > 2 and not self.line_edits[-2].text():
            removing_line_edit = self.line_edits.pop()
            removing_line_edit.deleteLater()
            removing_label = self.labels.pop()
            removing_label.deleteLater()
            self.labels[-1].setText("b")

            if len(self.line_edits) > 1:
                self.line_edits[-2].setDisabled(False)

    def new_line_edit_and_label(self) -> None:
        label = QLabel(self)
        label.setText("b")
        label_text = ""
        i = len(self.labels)

        while i > 0:
            label_text += SUBSCRIPT_NUMBERS[i%10]
            i = i // 10

        if self.labels:
            self.labels[-1].setText("x" + label_text)

        self.labels.append(label)
        self.horizontal_layout.addWidget(label)

        line_edit = QLineEdit(self)
        line_edit.editingFinished.connect(self.process_line_edit_finished)

        self.line_edits.append(line_edit)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(line_edit.sizePolicy().hasHeightForWidth())
        line_edit.setSizePolicy(sizePolicy)
        line_edit.setMaximumSize(QtCore.QSize(45, 16777215))
        line_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(r"(^$|0|-|^-?[1-9][0-9]*$)")))
        self.horizontal_layout.addWidget(line_edit)

    def set_disable_input(self, set_to_disabled: bool) -> None:
        i = -1
        ptr_line_edit = self.line_edits[i]

        while not ptr_line_edit.text():
            ptr_line_edit.setDisabled(set_to_disabled)
            i -= 1
            ptr_line_edit = self.line_edits[i]

        ptr_line_edit.setDisabled(set_to_disabled)

    def check_all_filled(self):
        try:
            # this needs an explanation: check if everything is valid int, turn it back to str so that 0 still evals to True
            return all(str(int(a.text())) for a in self.line_edits[:-1])
        except ValueError:
            return False


    def setup_ui(self) -> None:
        self.horizontal_layout = QHBoxLayout(self)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)

        line_edit = QLineEdit(self)
        line_edit.editingFinished.connect(self.process_line_edit_finished)

        self.line_edits.append(line_edit)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(line_edit.sizePolicy().hasHeightForWidth())
        line_edit.setSizePolicy(sizePolicy)
        line_edit.setMaximumSize(QtCore.QSize(45, 16777215))
        line_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(r"(^$|0|-|^-?[1-9][0-9]*$)")))
        self.horizontal_layout.addWidget(line_edit)

        self.new_line_edit_and_label()