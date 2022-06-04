import typing
from automaton.presburger import generate_equals_solver_automaton
from utils.transformers import transform_numbers_little_endian
import random
import time

def generate_coeffs(length: int, limit: int):
    res: typing.List[int] = []
    
    for _ in range(length):
        res.append(random.randint(-limit, limit))

    return res

def check_solution(formula: typing.List[int], x_vector: typing.List[int]):
    left_side = 0

    for i in range(len(x_vector)):
        left_side += formula[i] * x_vector[i]

    if formula[-1] > left_side:
        return 1

    if formula[-1] < left_side:
        return -1

    return 0

def benchmark(formula_length: int, formula_coeff_modulo_limit: int):
    result: typing.List[int] = []
    formula = generate_coeffs(formula_length, formula_coeff_modulo_limit)
    x_vector = generate_coeffs(formula_length - 1, formula_coeff_modulo_limit)
    manual_check_res = 0
    runs = 5

    start = time.perf_counter_ns()

    for _ in range(runs):
        manual_check_res = check_solution(formula, x_vector)

    result.append((time.perf_counter_ns() - start) // runs)


    start = time.perf_counter_ns()

    solving_automata = generate_equals_solver_automaton(formula, False)

    result.append(time.perf_counter_ns() - start)


    automata_input_list = transform_numbers_little_endian(x_vector)
    automata_input = [":".join(a) for a in zip(*automata_input_list)]


    start = time.perf_counter_ns()

    for _ in range(runs-1):
        solving_automata.run_on_input("|".join(automata_input))
        solving_automata.reset_state()
    solving_automata.run_on_input("|".join(automata_input))

    result.append((time.perf_counter_ns() - start) // runs)
    result.append(solving_automata.state_counter)

    return result


def benchmark_improved(formula_length: int, formula_coeff_modulo_limit: int):
    runs_amount = 100

    results = [benchmark(formula_length, formula_coeff_modulo_limit) for _ in range(runs_amount)]

    restructured_results = [[results[i][j] for i in range(len(results))] for j in range(len(results[0]))]

    final_results = [sum(a) // runs_amount for a in restructured_results]

    print(f"formula_length = {formula_length}, modulo_max = {formula_coeff_modulo_limit}")
    print(f"naive solve time: {final_results[0]}ns, automata build time: {final_results[1]}ns, automata solve time: {final_results[2]}ns, automata state amount: {final_results[3]}")

benchmark_improved(3, 10)
benchmark_improved(3, 20)
benchmark_improved(3, 40)
benchmark_improved(5, 10)
benchmark_improved(5, 20)
benchmark_improved(8, 10)
benchmark_improved(10, 10)
benchmark_improved(12, 7)
#benchmark_improved(15, 5)