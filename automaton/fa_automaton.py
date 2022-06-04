from __future__ import annotations

import typing

from automaton.base_automaton import AbstractState, AbstractAutomaton

class FAState(AbstractState):
    __slots__ = ("is_accepting", "transitions", "parent_automaton", "my_number", "result")

    is_accepting: bool

    def __init__(self, parent_automaton: FAAutomaton, is_accepting: bool, result: typing.Optional[str] = None):
        super().__init__(parent_automaton)
        self.is_accepting = is_accepting
        self.result = result

class FAAutomaton(AbstractAutomaton[FAState]):
    def __init__(self, initial_state_cls: typing.Type[FAState], is_initial_accepting: bool, result: typing.Optional[str] = None):
        super().__init__(initial_state_cls, is_initial_accepting, result)
        
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