from __future__ import annotations

import typing

from automaton.base_automaton import AbstractState, AbstractAutomaton

class FAState(AbstractState):
    is_accepting: bool

    def __init__(self, is_accepting: bool, result: typing.Optional[str] = None):
        super().__init__()
        self.is_accepting = is_accepting
        self.result = result

class FAAutomaton(AbstractAutomaton[FAState]):
    def check_accepting(self):
        if not self.current_state:
            return False

        return self.current_state.is_accepting

    def get_result(self):
        if not self.current_state:
            return None

        return self.current_state.result

    # to get right typing
    def change_state(self, input: str):
        super().change_state(input)

    def run_on_input(self, full_input: str) -> typing.Optional[str]:
        result = super().run_on_input(full_input)

        if self.check_accepting() is False:
            return None
        
        return result