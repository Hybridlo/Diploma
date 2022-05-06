from __future__ import annotations

import typing
from functools import partial
from PyQt6.QtCore import (QByteArray, QTimer)

from automaton.fa_automaton import FAAutomaton, FAState
from automata_graph.graph_render import RenderedAutomaton
from utils.const import ComparisonValues
from utils.transformers import transform_number
from widgets.resultholders import FourBasketResultHolder

if typing.TYPE_CHECKING:
    from main import Window
    from PyQt6.QtWidgets import QWidget
    from PyQt6.QtSvgWidgets import QSvgWidget
    from widgets.progressholders import VectorComparingProgress

def render_svg_step(r_automaton: RenderedAutomaton, target_widget: QSvgWidget, input: str, transition: bool = False):
    if not transition:
        xml_data = r_automaton.render_step()

    else:
        if not input:
            return

        xml_data = r_automaton.render_step(input[0])
        if "|" in input:
            r_automaton.automaton.change_state(input[:input.find('|')])
            input = input[input.find('|') + 1:]
        else:
            r_automaton.automaton.change_state(input)
            input = ""

    target_widget.load(QByteArray(xml_data))    # type: ignore

    QTimer.singleShot(2000, partial(render_svg_step, r_automaton, target_widget, input, not transition))

class VectorComparatorByCoordinate:
    def __init__(self, main_window: Window, progress_holder: VectorComparingProgress, result_holder: FourBasketResultHolder):
        self.solving_automaton = self._build_solving_automata()
        self.transition = False
        self.main_window = main_window
        self.progress_holder = progress_holder
        self.result_holder = result_holder
        self.pivot_vector: typing.List[int] = main_window.pivot_vector.vector_data
        self.current_comparing_vector: typing.Optional[typing.List[int]] = None
        self.current_comparing_vector_copy: typing.Optional[typing.List[int]] = None
        self.current_comparison_state: typing.List[str] = []
        self.current_pivot_coordinate: str = ""
        self.current_comparing_coordinate: str = ""

    def _build_solving_automata(self) -> RenderedAutomaton[FAState]:
        automaton = FAAutomaton(FAState, False)

        state_less = FAState(automaton, True, ComparisonValues.less)
        state_equal = FAState(automaton, True, ComparisonValues.equal)
        state_greater = FAState(automaton, True, ComparisonValues.greater)

        automaton.initial_state.set_transition("1:0", state_less)
        automaton.initial_state.set_transition("0:1", state_greater)
        automaton.initial_state.set_transition("1:1", state_equal)
        automaton.initial_state.set_transition("0:0", state_equal)

        state_equal.set_transition("0:0", state_equal)
        state_equal.set_transition("1:1", state_equal)
        state_equal.set_transition("0:1", state_less)
        state_equal.set_transition("1:0", state_greater)

        state_less.set_transition("0:0", state_less)
        state_less.set_transition("1:1", state_less)
        state_less.set_transition("0:1", state_less)
        state_less.set_transition("1:0", state_less)

        state_greater.set_transition("0:0", state_greater)
        state_greater.set_transition("1:1", state_greater)
        state_greater.set_transition("0:1", state_greater)
        state_greater.set_transition("1:0", state_greater)

        return RenderedAutomaton(automaton)

    def finalize_vector_compare(self):
        if not self.current_comparison_state or "-" in self.current_comparison_state or not self.current_comparing_vector_copy:
            raise Exception("finalizing impossible")

        elif ComparisonValues.greater in self.current_comparison_state and ComparisonValues.less in self.current_comparison_state:
            self.result_holder.add_result(self.current_comparing_vector_copy, 4)

        elif ComparisonValues.greater in self.current_comparison_state:
            self.result_holder.add_result(self.current_comparing_vector_copy, 2)

        elif ComparisonValues.less in self.current_comparison_state:
            self.result_holder.add_result(self.current_comparing_vector_copy, 1)

        else:
            self.result_holder.add_result(self.current_comparing_vector_copy, 3)
    
    def get_new_comparing_vector(self):
        if self.current_comparing_vector == []:
            self.finalize_vector_compare()
        
        getting_vector = self.main_window.defined_vectors[0]

        self.pivot_vector = self.main_window.pivot_vector.vector_data
        self.progress_holder.current_pivot_vector.setText(f"({', '.join(str(a) for a in self.pivot_vector)})")

        self.current_comparing_vector = getting_vector.vector_data
        self.current_comparing_vector_copy = self.current_comparing_vector.copy()
        self.progress_holder.current_comparing_vector.setText(f"({', '.join(str(a) for a in self.current_comparing_vector)})")

        self.current_comparison_state = ['-' for _ in self.current_comparing_vector]
        self.progress_holder.current_comparison_results.setText(f"({', '.join(a for a in self.current_comparison_state)})")

        self.main_window.remove_vector(getting_vector)

    def pop_vector_coordinates(self):
        if not self.current_comparing_vector:
            raise Exception("Can't get vector coordinate: comparing vector not defined")

        pivot_coord = self.pivot_vector.pop(0)
        compare_coord = self.current_comparing_vector.pop(0)

        pivot_sign, pivot_coord_binary = transform_number(pivot_coord)
        compare_sign, compare_coord_binary = transform_number(compare_coord)

        pivot_coord_binary = pivot_sign + pivot_coord_binary.rjust(len(compare_coord_binary), "0")
        compare_coord_binary = compare_sign + compare_coord_binary.rjust(len(pivot_coord_binary)-1, "0")

        self.current_pivot_coordinate = pivot_coord_binary + f" ({pivot_coord})"
        self.current_comparing_coordinate = compare_coord_binary + f" ({compare_coord})"

        self.progress_holder.current_pivot_vector_coordinate.setText(self.current_pivot_coordinate)
        self.progress_holder.current_comparing_vector_coordinate.setText(self.current_comparing_coordinate)

    def finalize_coord_compare(self):
        self.transition = False

        if not self.solving_automaton.automaton.current_state:
            raise Exception("Invalid state for result")

        self.res = self.solving_automaton.automaton.current_state.result

        if not self.res:
            raise Exception("State was not finalizing or doesn't have a result")

        res_position = self.current_comparison_state.index("-")

        self.current_comparison_state.pop(res_position)
        self.current_comparison_state.insert(res_position, self.res)

        self.progress_holder.current_comparison_results.setText(f"({', '.join(a for a in self.current_comparison_state)})")
        self.solving_automaton.automaton.reset_state()
    
    def do_transition(self):
        if not self.transition:
            xml_data = self.solving_automaton.render_step()

        else:
            pivot_bit = self.current_pivot_coordinate[0]
            self.current_pivot_coordinate = self.current_pivot_coordinate[1:]

            compare_bit = self.current_comparing_coordinate[0]
            self.current_comparing_coordinate = self.current_comparing_coordinate[1:]

            if pivot_bit == " ":
                self.finalize_coord_compare()
                self.current_pivot_coordinate = ""
                self.current_comparing_coordinate = ""
                return

            inp = compare_bit + ":" + pivot_bit
            xml_data = self.solving_automaton.render_step(inp)
            self.solving_automaton.automaton.change_state(inp)

            self.progress_holder.current_pivot_vector_coordinate.setText(self.current_pivot_coordinate)
            self.progress_holder.current_comparing_vector_coordinate.setText(self.current_comparing_coordinate)
            self.progress_holder.current_binary_comparing.setText(inp)

        self.main_window.svg_widget.load(QByteArray(xml_data))    # type: ignore

        self.transition = not self.transition
    
    def solution_step(self):
        if not self.main_window.defined_vectors and not self.current_comparing_vector and not self.current_comparing_coordinate:
            self.finalize_vector_compare()
            return

        elif not self.current_comparing_vector and not self.current_comparing_coordinate:
            self.get_new_comparing_vector()

        elif not self.current_comparing_coordinate:
            self.pop_vector_coordinates()

        else:
            self.do_transition()

        QTimer.singleShot(100, self.solution_step)