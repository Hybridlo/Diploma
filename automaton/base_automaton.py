from __future__ import annotations

import abc
import typing
import typing_extensions

_T = typing.TypeVar("_T", bound="AbstractState")

class AbstractState(abc.ABC):
    """Defines abstract automaton state
    override is_accepting to make automata an FA"""

    is_accepting: typing.Optional[bool]

    def __init__(self, parent_automaton: AbstractAutomaton):
        self.is_accepting: typing.Optional[bool] = None
        self.transitions: typing.Dict[str, typing.Tuple[typing_extensions.Self, typing.Optional[str]]] = {}
        self.parent_automaton: AbstractAutomaton = parent_automaton     #idk if i need it, but i do need a counter for them
        self.my_number = parent_automaton.state_counter
        parent_automaton.state_counter += 1

    def set_transition(self, transition_input: str, to_state: typing_extensions.Self, transition_output: typing.Optional[str] = None):
        self.transitions[transition_input] = (to_state, transition_output)


class AbstractAutomaton(typing.Generic[_T]):
    def __init__(self, initial_state_cls: typing.Type[_T], *args, **kwargs):
        """call super().__init__() before
        doing anything in inherited init"""
        self.state_counter: int = 0
        self.initial_state = initial_state_cls(self, *args, **kwargs)
        self.current_state: typing.Optional[_T] = self.initial_state

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