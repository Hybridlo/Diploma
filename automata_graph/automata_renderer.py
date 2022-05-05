from __future__ import annotations

import typing
from functools import partial
from PyQt6.QtCore import (QByteArray, QTimer)

from automaton.fa_automaton import FAAutomaton, FAState
from utils.const import ComparisonValues

if typing.TYPE_CHECKING:
    from main import Window
    from PyQt6.QtWidgets import QWidget
    from PyQt6.QtSvgWidgets import QSvgWidget
    from automata_graph.graph_render import RenderedAutomaton

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
    def __init__(self, main_window: Window):
        self.main_window = main_window

    def _build_solving_automata(self) -> RenderedAutomaton:
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