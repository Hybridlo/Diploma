from __future__ import annotations

import typing
from functools import partial
from PyQt6.QtCore import (QByteArray, QTimer, QSize)

from automaton.fa_automaton import FAAutomaton, FAState
from automata_graph.graph_render import RenderedAutomaton
from automaton.presburger import generate_equals_solver_automaton
from utils.const import ComparisonValues, HyperplaneComparisonValues
from utils.transformers import transform_number_big_endian, transform_numbers_little_endian
from widgets.hyperplane_compare.resultholder import ThreeBasketResultHolder
from widgets.vector_compare.resultholder import FourBasketResultHolder

if typing.TYPE_CHECKING:
    from widgets.vector_compare.vectorcomparer import VectorComparer
    from widgets.vector_compare.progressholder import VectorComparingProgress
    from widgets.hyperplane_compare.hyperplanecomparer import HyperplaneComparer
    from widgets.hyperplane_compare.progressholder import HyperplaneComparingProgress

class VectorComparatorByCoordinate:
    def __init__(self, comparer: VectorComparer, progress_holder: VectorComparingProgress, result_holder: FourBasketResultHolder):
        self.solving_automaton = self._build_solving_automata()
        self.transition = False
        self.comparer = comparer
        self.progress_holder = progress_holder
        self.result_holder = result_holder
        self.pivot_vector: typing.List[int] = comparer.pivot_vector.vector_data
        self.current_comparing_vector: typing.Optional[typing.List[int]] = None
        self.current_comparing_vector_copy: typing.Optional[typing.List[int]] = None
        self.current_comparison_state: typing.List[str] = []
        self.current_pivot_coordinate: str = ""
        self.current_comparing_coordinate: str = ""
        self.timer: QTimer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.solution_step)

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
        
        getting_vector = self.comparer.defined_vectors[0]

        self.pivot_vector = self.comparer.pivot_vector.vector_data
        self.progress_holder.current_pivot_vector.setText(f"({', '.join(str(a) for a in self.pivot_vector)})")

        self.current_comparing_vector = getting_vector.vector_data
        self.current_comparing_vector_copy = self.current_comparing_vector.copy()
        self.progress_holder.current_comparing_vector.setText(f"({', '.join(str(a) for a in self.current_comparing_vector)})")

        self.current_comparison_state = ['-' for _ in self.current_comparing_vector]
        self.progress_holder.current_comparison_results.setText(f"({', '.join(a for a in self.current_comparison_state)})")

        self.comparer.remove_vector(getting_vector)

    def pop_vector_coordinates(self):
        if not self.current_comparing_vector:
            raise Exception("Can't get vector coordinate: comparing vector not defined")

        pivot_coord = self.pivot_vector.pop(0)
        compare_coord = self.current_comparing_vector.pop(0)

        pivot_sign, pivot_coord_binary = transform_number_big_endian(pivot_coord)
        compare_sign, compare_coord_binary = transform_number_big_endian(compare_coord)

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
        if not self.transition and self.comparer.main_window.animation_time:
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

            if self.comparer.main_window.animation_time:
                xml_data = self.solving_automaton.render_step(inp)

            self.solving_automaton.automaton.change_state(inp)

            self.progress_holder.current_pivot_vector_coordinate.setText(self.current_pivot_coordinate)
            self.progress_holder.current_comparing_vector_coordinate.setText(self.current_comparing_coordinate)
            self.progress_holder.current_binary_comparing.setText(inp)

        if self.comparer.main_window.animation_time:
            self.comparer.main_window.svg_widget.load(QByteArray(xml_data))    # type: ignore
            self.comparer.main_window.svg_widget.setFixedSize(QSize(*self.solving_automaton.get_size()))

        self.transition = not self.transition
    
    def solution_step(self):
        if not self.comparer.defined_vectors and not self.current_comparing_vector and not self.current_comparing_coordinate:
            self.finalize_vector_compare()
            self.comparer.stop_automata()
            return

        elif not self.current_comparing_vector and not self.current_comparing_coordinate:
            self.get_new_comparing_vector()

        elif not self.current_comparing_coordinate:
            self.pop_vector_coordinates()

        else:
            self.do_transition()

        if not self.comparer.main_window.animation_time:
            self.timer.start(0)
        else:
            self.timer.start(self.comparer.main_window.animation_time)

class HyperplaneComparator:
    def __init__(self, comparer: HyperplaneComparer, progress_holder: HyperplaneComparingProgress, result_holder: ThreeBasketResultHolder):
        self.transition = False
        self.comparer = comparer
        self.progress_holder = progress_holder
        self.result_holder = result_holder
        self.formula: typing.List[int] = comparer.formula.formula_data
        self.current_comparing_vector: typing.Optional[typing.List[int]] = None
        self.current_comparison_state: str = ""
        self.current_comparing_vector_input: typing.Optional[typing.List[str]] = None
        self.solving_automaton = self._build_solving_automata()
        self.timer: QTimer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.solution_step)

    def _build_solving_automata(self) -> RenderedAutomaton[FAState]:
        return generate_equals_solver_automaton(self.formula)

    def finalize_vector_compare(self):
        if not self.current_comparing_vector:
            raise Exception("finalizing impossible")

        elif self.current_comparison_state == HyperplaneComparisonValues.accepted:
            self.result_holder.add_result(self.current_comparing_vector, 3)

        elif self.current_comparison_state == HyperplaneComparisonValues.rejected:
            self.result_holder.add_result(self.current_comparing_vector, 1)
    
    def get_new_comparing_vector(self):
        if self.current_comparing_vector_input == []:
            self.finalize_vector_compare()
        
        getting_vector = self.comparer.defined_vectors[0]

        self.formula = self.comparer.formula.formula_data
        self.progress_holder.current_formula.setText(f"({', '.join(str(a) for a in self.formula)})")

        self.current_comparing_vector = getting_vector.vector_data
        self.progress_holder.current_comparing_vector.setText(f"({', '.join(str(a) for a in self.current_comparing_vector)})")

        self.current_comparison_state = ""
        self.progress_holder.current_comparison_results.setText(f"{str(self.current_comparison_state)}")

        self.comparer.remove_vector(getting_vector)

        self.current_comparing_vector_input = [":".join(a) for a in zip(*transform_numbers_little_endian(self.current_comparing_vector))] + [""]

    def finalize_coord_compare(self):
        self.transition = False

        if not self.solving_automaton.automaton.current_state:
            self.current_comparison_state = HyperplaneComparisonValues.rejected

        else:
            if not self.solving_automaton.automaton.current_state.is_accepting:
                self.current_comparison_state = HyperplaneComparisonValues.rejected

        if not self.current_comparison_state:
            self.current_comparison_state = HyperplaneComparisonValues.accepted

        self.progress_holder.current_comparison_results.setText(f"{str(self.current_comparison_state)}")
        self.solving_automaton.automaton.reset_state()
    
    def do_transition(self):
        if not self.transition and self.comparer.main_window.animation_time:
            xml_data = self.solving_automaton.render_step()

        else:
            if not self.current_comparing_vector_input:
                raise Exception("List was unexpectedly empty")

            inp = self.current_comparing_vector_input.pop(0)

            if inp == "":
                self.finalize_coord_compare()
                return

            if self.comparer.main_window.animation_time:
                xml_data = self.solving_automaton.render_step(inp)

            self.solving_automaton.automaton.change_state(inp)

            self.progress_holder.current_binary_comparing.setText(inp)

        if self.comparer.main_window.animation_time:
            self.comparer.main_window.svg_widget.load(QByteArray(xml_data))    # type: ignore
            self.comparer.main_window.svg_widget.setFixedSize(QSize(*self.solving_automaton.get_size()))

        self.transition = not self.transition
    
    def solution_step(self):
        if not self.comparer.defined_vectors and not self.current_comparing_vector_input:
            self.finalize_vector_compare()
            self.comparer.stop_automata()
            return

        elif not self.current_comparing_vector_input:
            self.get_new_comparing_vector()

        else:
            self.do_transition()

        if not self.comparer.main_window.animation_time:
            self.timer.start(0)
        else:
            self.timer.start(self.comparer.main_window.animation_time)