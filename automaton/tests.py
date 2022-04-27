import unittest

from automaton.fa_automaton import FAAutomaton, FAState

class FAAutomatonTestCase(unittest.TestCase):
    def test_one(self):
        automaton = FAAutomaton(FAState, False)

        initial_state = automaton.initial_state
        q1 = FAState(automaton, False)
        q2 = FAState(automaton, True, "Done!")

        initial_state.set_transition("0", initial_state)
        initial_state.set_transition("1", q1)
        q1.set_transition("1", q2)
        q2.set_transition("1", q2)


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