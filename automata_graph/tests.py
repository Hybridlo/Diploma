import typing
import unittest

from automaton.fa_automaton import FAAutomaton, FAState
from automata_graph.graph_render import RenderedAutomaton

import xml.etree.cElementTree as cET

class RendererTestCase(unittest.TestCase):
    def test_one(self):
        automaton = FAAutomaton(FAState, False)

        initial_state = automaton.initial_state
        q1 = FAState(automaton, False)
        q2 = FAState(automaton, True, "Done!")

        initial_state.set_transition("0", initial_state)
        initial_state.set_transition("1", q1)
        q1.set_transition("1", q2)
        q2.set_transition("1", q2)

        r_automaton = RenderedAutomaton(automaton)

        steps_imgs: typing.List[bytes] = []

        input_step = "0"
        steps_imgs.append(r_automaton.render_step())
        steps_imgs.append(r_automaton.render_step(input_step))
        r_automaton.automaton.change_state(input_step)

        input_step = "1"
        steps_imgs.append(r_automaton.render_step())
        steps_imgs.append(r_automaton.render_step(input_step))
        r_automaton.automaton.change_state(input_step)

        input_step = "1"
        steps_imgs.append(r_automaton.render_step())
        steps_imgs.append(r_automaton.render_step(input_step))
        r_automaton.automaton.change_state(input_step)

        steps_imgs.append(r_automaton.render_step())

        counter = 0

        for img in steps_imgs:
            counter += 1
            with open(f"data_tests/step{counter}.svg", "r") as infile:
                self.assertEqual(img.decode("utf-8"), infile.read())