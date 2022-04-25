import unittest

from automaton.fa_automaton import FAAutomaton, FAState

class FAAutomatonTestCase(unittest.TestCase):
    def test_one(self):
        initial_state = FAState(False)
        q1 = FAState(False)
        q2 = FAState(True, "Done!")

        initial_state.set_transition("0", initial_state)
        initial_state.set_transition("1", q1)
        q1.set_transition("1", q2)
        q2.set_transition("1", q2)

        automaton = FAAutomaton(initial_state)

        automaton.run_on_input("0|1|1")
        self.assertTrue(automaton.check_accepting())
        self.assertEqual("Done!", automaton.get_result())

        automaton.reset_state()
        automaton.run_on_input("0|1")
        self.assertFalse(automaton.check_accepting())
        self.assertIsNone(automaton.get_result())

        automaton.reset_state()
        automaton.run_on_input("1|0")
        self.assertFalse(automaton.check_accepting())

        automaton.reset_state()
        automaton.run_on_input("1|1|0")
        self.assertFalse(automaton.check_accepting())