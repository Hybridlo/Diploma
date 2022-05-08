import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow
)
from automata_graph.graph_render import RenderedAutomaton
from automaton.fa_automaton import FAAutomaton, FAState

from main_ui import Ui_MainWindow
from widgets.vector_compare.vectorcomparer import VectorComparer

class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.vector_comparer = VectorComparer(self, self.tab)
        self.vector_comparer.setObjectName("vector_comparer")
        self.vector_comparer_layout.addWidget(self.vector_comparer)

    def execute_test(self):
        pass
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())