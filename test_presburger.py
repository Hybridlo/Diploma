import typing
from automaton.presburger import generate_equals_solver_automaton
from utils.transformers import transform_numbers_little_endian

def solve_formula(f: typing.List[int], a: typing.List[int]):
    b = f[-1]
    f = f[:-1]

    r = 0

    for i in range(len(f)):
        r += a[i]*f[i]

    if r > b:
        return 1

    if r == b:
        return 0

    return -1

if __name__ == "__main__":
    automaton = generate_equals_solver_automaton([2, -1, -1])
    for i in range(100):
        check_solution = [i, i*2+1]

        bits_solution = transform_numbers_little_endian(check_solution)

        automata_input = [":".join(a) for a in zip(*bits_solution)]
        for inp in automata_input:
            automaton.automaton.change_state(inp)

        if not (automaton.automaton.current_state and automaton.automaton.current_state.is_accepting):
            print("uh-oh")
            print(check_solution)
            print(bits_solution)
            if automaton.automaton.current_state:
                print(automaton.automaton.current_state.is_accepting)
            break
        automaton.automaton.reset_state()
    else:
        print("we're good... we're good")