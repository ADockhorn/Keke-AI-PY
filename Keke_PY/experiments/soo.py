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

from Keke_PY.search_agents.AStar import AStar
from Keke_PY.search_agents.HeuristicGuidedSearch import HeuristicGuidedSearch
from Keke_PY.experiments.RandomSamplingAlgorithm import RandomSamplingAlgorithm
from Keke_PY.experiments.BayesianOptimizationAlgorithm import BayesianOptimizationAlgorithm
from Keke_PY.experiments.KekeProblem import KekeProblem
from Keke_PY.heuristic_pymoo_representations.HeuristicTreeRepresentation import HeuristicTreeRepresentation
from Keke_PY.heuristic_pymoo_representations.TrackedRepresentation import TrackedRepresentation
from Keke_PY.heuristic_pymoo_representations.WeightedHeuristicSumRepresentation import WeightedHeuristicSumRepresentation


int_arguments: List[int] = []
for argument in sys.argv:
    if argument.isdigit():
        int_arguments.append(int(argument))

setups: [(bool, bool, int, bool)] = (
    #(False, False, 0, False),
    (False, True, 1, False),
    #(False, False, 2, False),
    #(False, False, 3, False),
    #(False, False, 4, False),

    #(False, False, 5, False),

    #(True, False, 0, False),
    #(True, True, 1, False),


    #(False, False, 0, True),
    (False, True, 1, True),
    #(False, False, 2, True),
    #(False, False, 3, True),
    #(False, False, 4, True),

    #(False, False, 5, True),

    #(True, False, 0, True),
    #(True, True, 1, True),
)
trees, track, algorithm, use_astar = setups[int_arguments[0]]

pop_size: int = 10
n_generations: int = 20


n_evals: int = pop_size * n_generations


representation = HeuristicTreeRepresentation(10) if trees else WeightedHeuristicSumRepresentation(0.5)
if track:
    representation = TrackedRepresentation(representation)

agent_factory = AStar.AStarFactory() if use_astar else HeuristicGuidedSearch.GuidedSearchFactory()

optimization_algorithm: Algorithm = [
    RandomSamplingAlgorithm(n_sample_points=n_evals, batch_size=pop_size, **representation.algorithm_arguments()),
    GA(pop_size=pop_size, **representation.algorithm_arguments()),
    DE(pop_size=pop_size),
    ES(n_offsprings=pop_size, pop_size=pop_size//2),
    PatternSearch(pop_size=pop_size, eliminate_duplicates=True),
    BayesianOptimizationAlgorithm(n_evals)
][algorithm]


test_problem = KekeProblem.default_problem(representation, multiprocessing.Pool(20), None, agent_factory)


def measure_time() -> Iterable[None]:
    start = time.time()
    yield None
    end = time.time()
    print("The time of execution is:", (end - start), "s")

if __name__ == '__main__':

    for _ in measure_time():
        info: List = [optimization_algorithm, representation, agent_factory]

        print("testing:", *info)



        res = minimize(
            test_problem,
            optimization_algorithm,
            termination=("n_eval", n_evals),
            verbose=True
        )


        print("testing done:", *info)
