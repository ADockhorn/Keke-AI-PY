from Keke_PY.experiments.BayesianOptimizationAlgorithm import BayesianOptimizationAlgorithm

if True:
    """Include Project root as Environment paths:"""
    from os.path import dirname, abspath
    import sys
    sys.path.append(dirname(dirname(dirname(abspath(__file__)))))


import multiprocessing
import time
from typing import Iterable, List

from pymoo.algorithms.soo.nonconvex.de import DE
from pymoo.algorithms.soo.nonconvex.es import ES
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.algorithms.soo.nonconvex.pattern import PatternSearch
from pymoo.core.algorithm import Algorithm
from pymoo.optimize import minimize

from Keke_PY.experiments.RandomSamplingAlgorithm import RandomSamplingAlgorithm
from Keke_PY.experiments.KekeProblem import KekeProblem
from Keke_PY.heuristic_pymoo_representations.HeuristicTreeRepresentation import HeuristicTreeRepresentation
from Keke_PY.heuristic_pymoo_representations.TrackedRepresentation import TrackedRepresentation
from Keke_PY.heuristic_pymoo_representations.WeightedHeuristicSumRepresentation import WeightedHeuristicSumRepresentation

int_arguments: List[int] = []
for argument in sys.argv:
    if argument.isdigit():
        int_arguments.append(int(argument))

setups: [(bool, bool, int)] = (
    (False, False, 0),
    (False, True, 1),
    (False, False, 2),
    (False, False, 3),
    (False, False, 4),
    # ! Working on bayesian !
    (False, False, 5),
    # ! Trees have some unresolved TODO@ask's !
    (True, False, 0),
    (True, True, 1),
)
trees, track, algorithm = setups[int_arguments[0]]

pop_size: int = 10
n_generations: int = 20


n_evals: int = pop_size * n_generations

representation = HeuristicTreeRepresentation(10) if trees else WeightedHeuristicSumRepresentation(0.5)
if track:
    representation = TrackedRepresentation(representation)


optimization_algorithm: Algorithm = [
    RandomSamplingAlgorithm(n_sample_points=n_evals, batch_size=pop_size, **representation.algorithm_arguments()),
    GA(pop_size=pop_size, **representation.algorithm_arguments()),
    DE(pop_size=pop_size),
    ES(n_offsprings=pop_size, pop_size=pop_size//2),
    PatternSearch(pop_size=pop_size, eliminate_duplicates=True),
    BayesianOptimizationAlgorithm(n_evals)
][algorithm]

test_problem = KekeProblem.default_problem(representation, multiprocessing.Pool(20), None)

def measure_time() -> Iterable[None]:
    start = time.time()
    yield None
    end = time.time()
    print("The time of execution is:", (end - start), "s")


if __name__ == '__main__':

    for _ in measure_time():

        print(f"testing {optimization_algorithm} ...")



        res = minimize(
            test_problem,
            optimization_algorithm,
            termination=("n_eval", n_evals),
            verbose=True
        )


        print(f"testing {optimization_algorithm} done")
