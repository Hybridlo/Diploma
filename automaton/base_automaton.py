from __future__ import annotations

import abc
import typing

_T = typing.TypeVar("_T", bound="AbstractState")

class AbstractState(abc.ABC):
    """Defines abstract automaton state
    override is_accepting to make automata an FA"""

    is_accepting: typing.Optional[bool]

    def __init__(self):
        self.is_accepting: typing.Optional[bool] = None
        self.transitions: typing.Dict[str, typing.Tuple[AbstractState, typing.Optional[str]]] = {}

    def set_transition(self, transition_input: str, to_state: AbstractState, transition_output: typing.Optional[str] = None):
        self.transitions[transition_input] = (to_state, transition_output)


class AbstractAutomaton(typing.Generic[_T]):
    def __init__(self, initial_state: _T):
        """call super().__init__() before
        doing anything in inherited init"""
        self.initial_state = initial_state
        self.current_state: typing.Optional[_T] = initial_state

    def change_state(self, inp: str) -> typing.Optional[str]:
        """changes current state of the automaton

        optionally returns a string for certain types
        of automata"""

        if not self.current_state:
            # we're in unidentified state, abort function
            return

        transition = self.current_state.transitions.get(inp)

        if not transition:
            # transition undefined, getting into unidentified state
            self.current_state = None
            return

        self.current_state = transition[0]
        
        return transition[1]

    def run_on_input(self, full_input: str) -> str:
        """full_input has to have inputs separated with
        "|" symbol"""

        result = ""

        for inp in full_input.split("|"):
            part_res = self.change_state(inp)

            if part_res:
                result += part_res

        return result

    def reset_state(self):
        self.current_state = self.initial_state