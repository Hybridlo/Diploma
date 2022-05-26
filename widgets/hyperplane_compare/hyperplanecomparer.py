from __future__ import annotations

import typing
from functools import partial
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QSizePolicy, QPushButton, QLabel, QVBoxLayout, QScrollArea, QMessageBox
)
from PyQt6 import QtCore
from automata_graph.automata_renderer import HyperplaneComparator
from widgets.hyperplane_compare.progressholder import HyperplaneComparingProgress
from widgets.hyperplane_compare.resultholder import ThreeBasketResultHolder

from widgets.vectordefiner import VectorDefinerFixed
from widgets.formuladefiner import FormulaDefiner
from widgets.vectordefined import VectorDefined

import random

if typing.TYPE_CHECKING:
    from main import Window

class HyperplaneComparer(QWidget):
    def __init__(self, main_window: Window, parent: typing.Optional['QWidget'] = ...) -> None:
        super().__init__(parent)
        self.setup_ui()
        self.main_window = main_window
        self.defined_vectors: typing.List[VectorDefined] = []
        self.result_widget: typing.Optional[ThreeBasketResultHolder] = None
        self.progress_widget: typing.Optional[HyperplaneComparingProgress] = None
        self.solver: typing.Optional[HyperplaneComparator] = None

        self.lock_button_react_binding()

    def lock_button_react_binding(self):
        self.formula.line_edits[0].editingFinished.connect(self.lock_button_react)

    def lock_button_react(self):
        if self.formula.line_edits[0].text():
            self.lock_formula_button.setDisabled(False)
        else:
            self.lock_formula_button.setDisabled(True)

    def lock_unlock_formula(self):
        _translate = QtCore.QCoreApplication.translate

        if not self.formula.check_all_filled():
            QMessageBox.warning(self, _translate("MainWindow", "Locking failed"), _translate("MainWindow", "Make sure all vector fields have numbers"))
            return

        last_line_edit = self.formula.line_edits[-1]
        self.vector_definer.resize_vector(self.formula.formula_size)

        if last_line_edit.isEnabled():
            self.lock_formula_button.setText(_translate("MainWindow", "Unlock"))
            self.formula.set_disable_input(True)
            self.vector_definer.set_disable_input(False)
            self.add_vector_button.setDisabled(False)
            self.vector_definer.fill_default()
        else:
            self.lock_formula_button.setText(_translate("MainWindow", "Lock"))
            self.formula.set_disable_input(False)
            self.vector_definer.set_disable_input(True)
            self.add_vector_button.setDisabled(True)


    def remove_vector(self, defined_vector: VectorDefined):
        self.defined_vectors.remove(defined_vector)
        defined_vector.deleteLater()

        if not self.defined_vectors and not self.solver:
            self.run_button.setDisabled(True)

    def add_vector_action(self):
        if not self.vector_definer.check_all_filled():
            _translate = QtCore.QCoreApplication.translate
            QMessageBox.warning(self, _translate("MainWindow", "Adding failed"), _translate("MainWindow", "Make sure all vector fields have numbers"))
            return

        self.add_vector(self.vector_definer.vector_data)

    def add_vector(self, vector_data: typing.List[int]):
        if not self.defined_vectors:
            self.run_button.setDisabled(False)

        new_defined_vector = VectorDefined(vector_data, self.added_vectors_area)
        self.added_vectors_layout.addWidget(new_defined_vector)
        new_defined_vector.pushButton.clicked.connect(partial(self.remove_vector, new_defined_vector))
        self.defined_vectors.append(new_defined_vector)

    def run_abort_automata(self):
        _translate = QtCore.QCoreApplication.translate

        if not self.solver:
            self.run_button.setText(_translate("MainWindow", "Abort"))
            self.pause_button.setText(_translate("MainWindow", "Pause"))
            self.add_vector_button.setDisabled(True)
            self.lock_formula_button.setDisabled(True)
            self.reset_button.setDisabled(True)
            self.test_button.setDisabled(True)
            self.pause_button.setDisabled(False)
            self.main_window.tabWidget.tabBar().setDisabled(True)
            
            self.main_window.clear_result_and_progress()
            self.progress_widget = HyperplaneComparingProgress(self.main_window.solving_progress_holder)
            self.main_window.solving_progress_layout.addWidget(self.progress_widget)
            self.result_widget = ThreeBasketResultHolder(self.main_window.result_widget_holder)
            self.main_window.result_layout_holder.addWidget(self.result_widget)
            self.solver = HyperplaneComparator(self, self.progress_widget, self.result_widget)
            self.solver.solution_step()
            self.main_window.svg_widget.setFixedSize(QtCore.QSize(*self.solver.solving_automaton.get_size()))

        else:
            self.stop_automata()

    def stop_automata(self):
        _translate = QtCore.QCoreApplication.translate

        self.main_window.svg_widget.load(QtCore.QByteArray(b""))     # type: ignore

        if self.solver and self.solver.timer:
            if self.solver.timer.isActive():
                self.solver.timer.stop()

        self.solver = None
        self.main_window.tabWidget.tabBar().setDisabled(False)
        self.pause_button.setDisabled(True)
        self.lock_formula_button.setDisabled(False)
        self.run_button.setDisabled(True)
        self.reset_button.setDisabled(False)
        self.test_button.setDisabled(False)
        self.main_window.tabWidget.setDisabled(False)
        self.run_button.setText(_translate("MainWindow", "Run"))

        while self.defined_vectors:
            self.remove_vector(self.defined_vectors[0])

        self.lock_unlock_formula()

    def pause_resume_automata(self):
        _translate = QtCore.QCoreApplication.translate

        if self.solver and self.solver.timer:
            if self.solver.timer.isActive():
                self.pause_button.setText(_translate("MainWindow", "Resume"))
                self.solver.timer.stop()
            else:
                self.pause_button.setText(_translate("MainWindow", "Pause"))
                self.solver.timer.start()

    def clear_inputs(self):
        if not self.formula.line_edits[-1].isEnabled():
            self.lock_unlock_formula()

        while self.defined_vectors:
            self.remove_vector(self.defined_vectors[0])

        self.formula.line_edits[0].setText("")
        self.formula.line_edits[-1].setText("")
        while self.formula.formula_size:
            self.formula.line_edits[-2].setText("")
            self.formula.process_line_edit_finished()

        self.lock_button_react()

    def create_test_data(self):
        self.clear_inputs()

        for i in range(3):
            self.formula.line_edits[i].setText(str(random.randrange(-2, 3)))
            self.formula.process_line_edit_finished()

        for i in range(-2, 3):
            for j in range(-2, 3):
                self.add_vector([i, j])

        self.lock_unlock_formula()
    

    def setup_ui(self):
        self.verticalLayout_10 = QVBoxLayout(self)
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_10.setSpacing(0)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.widget_10 = QWidget(self)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(4)
        sizePolicy.setHeightForWidth(self.widget_10.sizePolicy().hasHeightForWidth())
        self.widget_10.setSizePolicy(sizePolicy)
        self.widget_10.setObjectName("widget_10")
        self.verticalLayout_8 = QVBoxLayout(self.widget_10)
        self.verticalLayout_8.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout_8.setSpacing(2)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.widget_6 = QWidget(self.widget_10)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.widget_6.sizePolicy().hasHeightForWidth())
        self.widget_6.setSizePolicy(sizePolicy)
        self.widget_6.setObjectName("widget_6")
        self.verticalLayout_6 = QVBoxLayout(self.widget_6)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.widget_11 = QWidget(self.widget_6)
        self.widget_11.setObjectName("widget_11")
        self.horizontalLayout_5 = QHBoxLayout(self.widget_11)
        self.horizontalLayout_5.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.scrollArea = QScrollArea(self.widget_11)
        self.scrollArea.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents_6 = QWidget()
        self.scrollAreaWidgetContents_6.setGeometry(QtCore.QRect(0, 0, 352, 69))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollAreaWidgetContents_6.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents_6.setSizePolicy(sizePolicy)
        self.scrollAreaWidgetContents_6.setObjectName("scrollAreaWidgetContents_6")
        self.horizontalLayout_8 = QHBoxLayout(self.scrollAreaWidgetContents_6)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.formula = FormulaDefiner(self.scrollAreaWidgetContents_6)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.formula.sizePolicy().hasHeightForWidth())
        self.formula.setSizePolicy(sizePolicy)
        self.formula.setObjectName("pivot_vector")
        self.horizontalLayout_8.addWidget(self.formula, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents_6)
        self.horizontalLayout_5.addWidget(self.scrollArea)
        self.verticalLayout_6.addWidget(self.widget_11)
        self.widget_12 = QWidget(self.widget_6)
        self.widget_12.setObjectName("widget_12")
        self.horizontalLayout_4 = QHBoxLayout(self.widget_12)
        self.horizontalLayout_4.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.widget_13 = QWidget(self.widget_12)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_13.sizePolicy().hasHeightForWidth())
        self.widget_13.setSizePolicy(sizePolicy)
        self.widget_13.setObjectName("widget_13")
        self.horizontalLayout_6 = QHBoxLayout(self.widget_13)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label = QLabel(self.widget_13)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout_6.addWidget(self.label)
        self.horizontalLayout_4.addWidget(self.widget_13)
        self.lock_formula_button = QPushButton(self.widget_12)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lock_formula_button.sizePolicy().hasHeightForWidth())
        self.lock_formula_button.setSizePolicy(sizePolicy)
        self.lock_formula_button.setObjectName("lock_pivot_button")
        self.lock_formula_button.setDisabled(True)
        self.horizontalLayout_4.addWidget(self.lock_formula_button)
        self.verticalLayout_6.addWidget(self.widget_12)
        self.verticalLayout_8.addWidget(self.widget_6)
        self.widget_7 = QWidget(self.widget_10)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.widget_7.sizePolicy().hasHeightForWidth())
        self.widget_7.setSizePolicy(sizePolicy)
        self.widget_7.setObjectName("widget_7")
        self.verticalLayout_7 = QVBoxLayout(self.widget_7)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.widget_15 = QWidget(self.widget_7)
        self.widget_15.setObjectName("widget_15")
        self.horizontalLayout_10 = QHBoxLayout(self.widget_15)
        self.horizontalLayout_10.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.scrollArea_2 = QScrollArea(self.widget_15)
        self.scrollArea_2.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea_2.sizePolicy().hasHeightForWidth())
        self.scrollArea_2.setSizePolicy(sizePolicy)
        self.scrollArea_2.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.scrollAreaWidgetContents_7 = QWidget()
        self.scrollAreaWidgetContents_7.setGeometry(QtCore.QRect(0, 0, 352, 69))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollAreaWidgetContents_7.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents_7.setSizePolicy(sizePolicy)
        self.scrollAreaWidgetContents_7.setObjectName("scrollAreaWidgetContents_7")
        self.horizontalLayout_11 = QHBoxLayout(self.scrollAreaWidgetContents_7)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.vector_definer = VectorDefinerFixed(self.scrollAreaWidgetContents_7)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.vector_definer.sizePolicy().hasHeightForWidth())
        self.vector_definer.setSizePolicy(sizePolicy)
        self.vector_definer.setObjectName("vector_definer")
        self.horizontalLayout_11.addWidget(self.vector_definer, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_7)
        self.horizontalLayout_10.addWidget(self.scrollArea_2)
        self.verticalLayout_7.addWidget(self.widget_15)
        self.widget_17 = QWidget(self.widget_7)
        self.widget_17.setObjectName("widget_17")
        self.horizontalLayout_13 = QHBoxLayout(self.widget_17)
        self.horizontalLayout_13.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.widget_18 = QWidget(self.widget_17)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_18.sizePolicy().hasHeightForWidth())
        self.widget_18.setSizePolicy(sizePolicy)
        self.widget_18.setObjectName("widget_18")
        self.horizontalLayout_14 = QHBoxLayout(self.widget_18)
        self.horizontalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_14.setSpacing(0)
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.label_2 = QLabel(self.widget_18)
        self.label_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_14.addWidget(self.label_2)
        self.horizontalLayout_13.addWidget(self.widget_18)
        self.add_vector_button = QPushButton(self.widget_17)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.add_vector_button.sizePolicy().hasHeightForWidth())
        self.add_vector_button.setSizePolicy(sizePolicy)
        self.add_vector_button.setObjectName("add_vector_button")
        self.horizontalLayout_13.addWidget(self.add_vector_button)
        self.verticalLayout_7.addWidget(self.widget_17)
        self.verticalLayout_8.addWidget(self.widget_7)
        self.label_3 = QLabel(self.widget_10)
        self.label_3.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_8.addWidget(self.label_3)
        self.scrollArea_3 = QScrollArea(self.widget_10)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(8)
        sizePolicy.setHeightForWidth(self.scrollArea_3.sizePolicy().hasHeightForWidth())
        self.scrollArea_3.setSizePolicy(sizePolicy)
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollArea_3.setObjectName("scrollArea_3")
        self.scrollAreaWidgetContents_8 = QWidget()
        self.scrollAreaWidgetContents_8.setGeometry(QtCore.QRect(0, 0, 370, 534))
        self.scrollAreaWidgetContents_8.setObjectName("scrollAreaWidgetContents_8")
        self.verticalLayout_9 = QVBoxLayout(self.scrollAreaWidgetContents_8)
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.added_vectors_area = QWidget(self.scrollAreaWidgetContents_8)
        self.added_vectors_area.setObjectName("added_vectors_area")
        self.added_vectors_layout = QVBoxLayout(self.added_vectors_area)
        self.added_vectors_layout.setContentsMargins(4, 4, 4, 4)
        self.added_vectors_layout.setSpacing(2)
        self.added_vectors_layout.setObjectName("added_vectors_layout")
        self.verticalLayout_9.addWidget(self.added_vectors_area, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_8)
        self.verticalLayout_8.addWidget(self.scrollArea_3)
        self.widget_3 = QWidget(self.widget_10)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_3.sizePolicy().hasHeightForWidth())
        self.widget_3.setSizePolicy(sizePolicy)
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout = QHBoxLayout(self.widget_3)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.test_button = QPushButton(self.widget_3)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.test_button.sizePolicy().hasHeightForWidth())
        self.test_button.setSizePolicy(sizePolicy)
        self.test_button.setObjectName("test_button")
        self.horizontalLayout.addWidget(self.test_button)
        self.reset_button = QPushButton(self.widget_3)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reset_button.sizePolicy().hasHeightForWidth())
        self.reset_button.setSizePolicy(sizePolicy)
        self.reset_button.setObjectName("reset_button")
        self.horizontalLayout.addWidget(self.reset_button)
        self.widget_5 = QWidget(self.widget_3)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_5.sizePolicy().hasHeightForWidth())
        self.widget_5.setSizePolicy(sizePolicy)
        self.widget_5.setObjectName("widget_5")
        self.horizontalLayout.addWidget(self.widget_5)
        self.pause_button = QPushButton(self.widget_3)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pause_button.sizePolicy().hasHeightForWidth())
        self.pause_button.setSizePolicy(sizePolicy)
        self.pause_button.setObjectName("pause_button")
        self.pause_button.setDisabled(True)
        self.horizontalLayout.addWidget(self.pause_button)
        self.run_button = QPushButton(self.widget_3)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.run_button.sizePolicy().hasHeightForWidth())
        self.run_button.setSizePolicy(sizePolicy)
        self.run_button.setObjectName("run_button")
        self.run_button.setDisabled(True)
        self.horizontalLayout.addWidget(self.run_button)
        self.verticalLayout_8.addWidget(self.widget_3)
        self.verticalLayout_10.addWidget(self.widget_10)

        self.lock_formula_button.clicked.connect(self.lock_unlock_formula)
        self.add_vector_button.clicked.connect(self.add_vector_action)
        self.run_button.clicked.connect(self.run_abort_automata)
        self.pause_button.clicked.connect(self.pause_resume_automata)
        self.reset_button.clicked.connect(self.clear_inputs)
        self.test_button.clicked.connect(self.create_test_data)
        
        self.retranslate_ui()

    def retranslate_ui(self):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("MainWindow", "Pivot vector"))
        self.lock_formula_button.setText(_translate("MainWindow", "Lock"))
        self.label_2.setText(_translate("MainWindow", "Add vector to set"))
        self.add_vector_button.setText(_translate("MainWindow", "Add"))
        self.label_3.setText(_translate("MainWindow", "Added vectors"))
        self.test_button.setText(_translate("MainWindow", "Test"))
        self.pause_button.setText(_translate("MainWindow", "Pause"))
        self.run_button.setText(_translate("MainWindow", "Run"))
        self.reset_button.setText(_translate("MainWindow", "Reset"))