import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox
)
from automata_graph.graph_render import RenderedAutomaton
from automaton.fa_automaton import FAAutomaton, FAState
from automata_graph.ui_renderer import render_svg_animation

from main_ui import Ui_MainWindow

class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

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

        render_svg_animation(r_automaton, self.widget_5, "0|1|1")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())