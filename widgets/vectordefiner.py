import typing
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QSizePolicy, QLineEdit
)
from PyQt6 import QtCore, QtGui

class VectorDefiner(QWidget):
    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.line_edits: typing.List[QLineEdit] = []
        self.setup_ui()

    @property
    def vector_size(self) -> int:
        return len(self.line_edits) - 1

    @property
    def vector_data(self) -> typing.List[int]:
        result: typing.List[int] = []

        for line_edit in self.line_edits:
            num_text = line_edit.text()
            if num_text:
                result.append(int(num_text))

        return result

    def new_line_edit(self, line_edit: typing.Optional[QLineEdit] = None) -> None:
        if not line_edit:
            line_edit = QLineEdit(self)

        self.line_edits.append(line_edit)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(line_edit.sizePolicy().hasHeightForWidth())
        line_edit.setSizePolicy(sizePolicy)
        line_edit.setMaximumSize(QtCore.QSize(60, 16777215))
        line_edit.setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(r"(^$|0|-|^-?[1-9][0-9]*$)")))
        self.horizontal_layout.addWidget(line_edit)

    def setup_ui(self) -> None:
        self.horizontal_layout = QHBoxLayout(self)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.new_line_edit()

class VectorDefinerAutoextend(VectorDefiner):
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

    def set_disable_input(self, set_to_disabled: bool) -> None:
        i = -1
        ptr_line_edit = self.line_edits[i]

        while not ptr_line_edit.text():
            ptr_line_edit.setDisabled(set_to_disabled)
            i -= 1
            ptr_line_edit = self.line_edits[i]

        ptr_line_edit.setDisabled(set_to_disabled)

    def new_line_edit(self) -> None:
        line_edit = QLineEdit(self)
        line_edit.editingFinished.connect(self.process_line_edit_finished)
        return super().new_line_edit(line_edit)

    def check_all_filled(self):
        try:
            # this needs an explanation: check if everything is valid int, turn it back to str so that 0 still evals to True
            return all(str(int(a.text())) for a in self.line_edits[:-1])
        except ValueError:
            return False

class VectorDefinerFixed(VectorDefiner):
    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.set_disable_input(True)

    def resize_vector(self, amount: int):
        while len(self.line_edits) > amount:
            removing = self.line_edits.pop()
            removing.deleteLater()

        while len(self.line_edits) < amount:
            self.new_line_edit()

    def set_disable_input(self, set_to_disabled: bool):
        for line_edit in self.line_edits:
            line_edit.setDisabled(set_to_disabled)

    def fill_default(self):
        for line_edit in self.line_edits:
            line_edit.setText("0")

    def check_all_filled(self):
        try:
            # this needs an explanation: check if everything is valid int, turn it back to str so that 0 still evals to True
            return all(str(int(a.text())) for a in self.line_edits)
        except ValueError:
            return False