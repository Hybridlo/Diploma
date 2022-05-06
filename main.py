import sys
import typing
from functools import partial
from PyQt6 import QtCore
from PyQt6.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox, QWidget
)
from automata_graph.graph_render import RenderedAutomaton
from automaton.fa_automaton import FAAutomaton, FAState
from automata_graph.automata_renderer import VectorComparatorByCoordinate, render_svg_step
from widgets.progressholders import VectorComparingProgress

from widgets.vectordefined import VectorDefined
from widgets.resultholders import FourBasketResultHolder

from main_ui import Ui_MainWindow

class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.defined_vectors: typing.List[VectorDefined] = []
        self.result_widget: typing.Optional[QWidget] = None     #prob still need an abstract for this
        self.progress_widget: typing.Optional[QWidget] = None

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.add_vector_button.setDisabled(True)
        self.lock_pivot_button.setDisabled(True)
        self.pivot_vector.line_edits[0].editingFinished.connect(self.lock_button_react)

    def execute_test(self):
        automaton = FAAutomaton(FAState, False)

        initial_state = automaton.initial_state
        q1 = FAState(automaton, False)
        q2 = FAState(automaton, True, "Done!")

        initial_state.set_transition("0", initial_state)
        initial_state.set_transition("1", q1)
        q1.set_transition("1", q2)
        q2.set_transition("1", q2)

        r_automaton = RenderedAutomaton(automaton)

        render_svg_step(r_automaton, self.svg_widget, "0|1|1")

    def lock_button_react(self):
        first_vector_line_edit = self.pivot_vector.line_edits[0]

        if first_vector_line_edit.text():
            self.lock_pivot_button.setDisabled(False)
        else:
            self.lock_pivot_button.setDisabled(True)

    def lock_pivot(self):
        if not self.pivot_vector.check_all_filled():
            _translate = QtCore.QCoreApplication.translate
            QMessageBox.warning(self, _translate("MainWindow", "Locking failed"), _translate("MainWindow", "Make sure all vector fields have numbers"))
            return

        last_line_edit = self.pivot_vector.line_edits[-1]
        _translate = QtCore.QCoreApplication.translate
        self.vector_definer.resize_vector(self.pivot_vector.vector_size)

        if last_line_edit.isEnabled():
            self.lock_pivot_button.setText(_translate("MainWindow", "Unlock"))
            self.pivot_vector.set_disable_input(True)
            self.vector_definer.set_disable_input(False)
            self.add_vector_button.setDisabled(False)
            self.vector_definer.fill_default()
        else:
            self.lock_pivot_button.setText(_translate("MainWindow", "Lock"))
            self.pivot_vector.set_disable_input(False)
            self.vector_definer.set_disable_input(True)
            self.add_vector_button.setDisabled(True)


    def remove_vector(self, defined_vector: VectorDefined):
        self.defined_vectors.remove(defined_vector)
        defined_vector.deleteLater()

    def add_vector(self):
        if not self.vector_definer.check_all_filled():
            _translate = QtCore.QCoreApplication.translate
            QMessageBox.warning(self, _translate("MainWindow", "Adding failed"), _translate("MainWindow", "Make sure all vector fields have numbers"))
            return

        new_defined_vector = VectorDefined(self.vector_definer.vector_data, self.added_vectors_area)
        self.added_vectors_layout.addWidget(new_defined_vector)
        new_defined_vector.pushButton.clicked.connect(partial(self.remove_vector, new_defined_vector))
        self.defined_vectors.append(new_defined_vector)

    def run_automata(self):
        self.run_button.setDisabled(True)
        self.add_vector_button.setDisabled(True)
        self.result_widget = FourBasketResultHolder(self.result_widget_holder)
        self.result_layout_holder.addWidget(self.result_widget)
        self.progress_widget = VectorComparingProgress(self.solving_progress_holder)
        self.solving_progress_layout.addWidget(self.progress_widget)
        self.solver = VectorComparatorByCoordinate(self, self.progress_widget, self.result_widget)
        self.solver.solution_step()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())