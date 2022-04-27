import typing
import unittest

from automaton.fa_automaton import FAAutomaton, FAState
from automata_graph.graph_render import RenderedAutomaton

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
        steps_imgs.extend(r_automaton.render(input_step))
        r_automaton.automaton.change_state(input_step)

        input_step = "1"
        steps_imgs.extend(r_automaton.render(input_step))
        r_automaton.automaton.change_state(input_step)

        input_step = "1"
        steps_imgs.extend(r_automaton.render(input_step))
        r_automaton.automaton.change_state(input_step)

        steps_imgs.extend(r_automaton.render())

        counter = 0

        for img in steps_imgs:
            counter += 1
            with open(f"step{counter}.png", "wb+") as outfile:
                outfile.write(img)