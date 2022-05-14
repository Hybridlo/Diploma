import sys
import typing
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QAbstractButton
)
from automata_graph.graph_render import RenderedAutomaton
from automaton.fa_automaton import FAAutomaton, FAState

from main_ui import Ui_MainWindow
from widgets.hyperplane_compare.hyperplanecomparer import HyperplaneComparer
from widgets.vector_compare.vectorcomparer import VectorComparer

class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.animation_time: typing.Optional[int] = 1000

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.vector_comparer = VectorComparer(self, self.tab)
        self.vector_comparer.setObjectName("vector_comparer")
        self.vector_comparer_layout.addWidget(self.vector_comparer)

        self.hyperplane_comparer = HyperplaneComparer(self, self.tab_2)
        self.hyperplane_comparer_layout.addWidget(self.hyperplane_comparer)

        self.button_group.buttonClicked.connect(self.change_animation_delay)

    def execute_test(self):
        pass

    def change_animation_delay(self, button: QAbstractButton):
        if button is self.button_x1:
            self.animation_time = 1000
        
        elif button is self.button_x2:
            self.animation_time = 500

        elif button is self.button_x4:
            self.animation_time = 250

        elif button is self.button_x8:
            self.animation_time = 125

        elif button is self.button_off:
            self.animation_time = None
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())