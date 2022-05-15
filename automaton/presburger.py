import typing
import itertools
from automaton.fa_automaton import FAAutomaton, FAState
from automata_graph.automata_renderer import RenderedAutomaton
from utils.const import ComparisonValues


def calc_formula_product(bits: str, coeffs: typing.List[int]):
    """
    helper formula for calculating a₁x₁ + a₂x₂ + a₃x₃ + ... + aₙxₙ
    where a are bits, either 0 or 1
    """
    bits = "".join(bits.split(":"))
    if len(bits) != len(coeffs):
        raise Exception("bits and coefficients are not matching")

    result = 0

    for i in range(0, len(bits)):
        result += int(bits[i]) * coeffs[i]

    return result

def generate_equals_solver_automaton(formula: typing.List[int]) -> RenderedAutomaton[FAState]:
    """
    takes in an equation formula in a form of list of ints

    a formula looking like this a₁x₁ + a₂x₂ + a₃x₃ + ... + aₙxₙ = b
    is passed as a list of coefficient, like this: [a₁, a₂, a₃, ..., aₙ, b]
    the b coefficient is always last and must be specified
    """
    if len(formula) < 2:
        raise Exception("Coefficients list is too small")

    # i'll be more explicit here
    automaton = FAAutomaton(FAState, False)
    automaton.initial_state.result = str(formula[-1])
    x_coeff_amount = len(formula) - 1
    unprocessed = [automaton.initial_state]
    processed: typing.List[FAState] = []
    # tuple of a states which should point to an accepting one and the transition string
    accepting_states_0: typing.List[typing.Tuple[FAState, str]] = []
    accepting_states_others: typing.List[typing.Tuple[FAState, str]] = []

    LEFTOVER_MARKER = "."

    while unprocessed:
        ptr_state = unprocessed.pop(0)

        if ptr_state.result is None:
            raise Exception("State result is not defined")

        processed.append(ptr_state)
        state_num = int(ptr_state.result.strip(LEFTOVER_MARKER))

        for a in [":".join(t) for t in itertools.product('01', repeat=x_coeff_amount)]:
            state_minus = state_num - calc_formula_product(a, formula[:-1])

            if state_minus % 2 == 0 and LEFTOVER_MARKER not in ptr_state.result:
                state_plus = state_num + calc_formula_product(a, formula[:-1])

                if state_plus == 0:
                    accepting_states_0.append((ptr_state, a))

                elif state_plus > 0:
                    accepting_states_others.append((ptr_state, a))

                existing_state = next((a for a in processed + unprocessed if a.result and a.result == str(state_minus // 2)), None)

                if not existing_state:
                    existing_state = FAState(automaton, False, str(state_minus // 2))
                    unprocessed.append(existing_state)

                ptr_state.set_transition(a, existing_state)

            else:
                state_plus = state_num + calc_formula_product(a, formula[:-1])

                if state_plus >= 0:
                    accepting_states_others.append((ptr_state, a))

                existing_state = next((a for a in processed + unprocessed if a.result and a.result == (str(state_minus // 2)) + LEFTOVER_MARKER), None)

                if not existing_state:
                    existing_state = FAState(automaton, False, str(state_minus // 2) + LEFTOVER_MARKER)
                    unprocessed.append(existing_state)

                ptr_state.set_transition(a, existing_state)

    for state, transition in accepting_states_0:
        accepting_state = FAState(automaton, True, ComparisonValues.equal)
        old_transition_state, res = state.transitions[transition]       # res will always be None, but let it be

        state.set_transition(transition, accepting_state)
        accepting_state.transitions = state.transitions

        if old_transition_state is not state:
            accepting_state.transitions[transition] = (old_transition_state, res)

    for state, transition in accepting_states_others:
        accepting_state = FAState(automaton, True, ComparisonValues.greater)
        old_transition_state, res = state.transitions[transition]       # res will always be None, but let it be

        state.set_transition(transition, accepting_state)
        accepting_state.transitions = state.transitions

        if old_transition_state is not state:
            accepting_state.transitions[transition] = (old_transition_state, res)

    return RenderedAutomaton(automaton)