from __future__ import annotations

import typing
from functools import partial
from PyQt6.QtWidgets import QApplication
from PyQt6 import (QtSvg, QtGui)
from PyQt6.QtCore import (QByteArray, QTimer)

if typing.TYPE_CHECKING:
    from PyQt6.QtSvgWidgets import QSvgWidget
    from automata_graph.graph_render import RenderedAutomaton

def render_svg_animation(r_automaton: RenderedAutomaton, target_widget: QSvgWidget, input: str, transition: bool = False):
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

    QTimer.singleShot(1000, partial(render_svg_animation, r_automaton, target_widget, input, not transition))