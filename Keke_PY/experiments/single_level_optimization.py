if True:
    """Include Project root as Environment paths:"""
    from os.path import dirname, abspath
    import sys
    sys.path.append(dirname(dirname(dirname(abspath(__file__)))))


import multiprocessing
import time
from typing import Iterable, List, Tuple

from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.core.algorithm import Algorithm
from pymoo.optimize import minimize

from Keke_PY.search_agents.AStar import AStar
from Keke_PY.search_agents.HeuristicGuidedSearch import HeuristicGuidedSearch
from Keke_PY.experiments.KekeProblem import KekeProblem
from Keke_PY.heuristic_pymoo_representations.HeuristicTreeRepresentation import HeuristicTreeRepresentation
from Keke_PY.heuristic_pymoo_representations.TrackedRepresentation import TrackedRepresentation
from Keke_PY.keke_game.simulation import load_level_set


int_arguments: List[int] = []
for argument in sys.argv:
    if argument.isdigit():
        int_arguments.append(int(argument))

level_nr = int_arguments[0]

use_astar: bool = False

pop_size: int = 10
n_generations: int = 20


n_evals: int = pop_size * n_generations


representation = TrackedRepresentation(HeuristicTreeRepresentation(10))

agent_factory = AStar.AStarFactory() if use_astar else HeuristicGuidedSearch.GuidedSearchFactory()

executor=multiprocessing.Pool(10)

optimization_algorithm: Algorithm = GA(pop_size=pop_size, **representation.algorithm_arguments())

levels: List[str] = [
    *[level["ascii"] for level in
      load_level_set("./json_levels/train_LEVELS.json")["levels"]],
    *[level["ascii"] for level in
      load_level_set("./json_levels/test_LEVELS.json")["levels"]],
]
level: str = levels[level_nr]



def measure_time() -> Iterable[None]:
    start = time.time()
    yield None
    end = time.time()
    print("The time of execution is:", (end - start), "s")

if __name__ == '__main__':

    training_problem: KekeProblem = KekeProblem(
        training_batches=[[level]],
        representation=representation,
        max_node_expansions=2000,
        executor=executor,
        test_batch=[],
        agent_factory=agent_factory
    )

    for _ in measure_time():
        info: List = [optimization_algorithm, representation, agent_factory]

        print(f"TRAINING ON LEVEL:{level_nr}")
        print(f"of {len(levels)} levels")
        print(f"---LEVEL STRING---\n{level}\n---LEVEL STRING---")



        res = minimize(
            training_problem,
            optimization_algorithm,
            termination=("n_eval", n_evals),
            verbose=True
        )


        print(f"TRAINING ON LEVEL:{level_nr}")
        print(f"of {len(levels)} levels")
        print(f"---LEVEL STRING---\n{level}\n---LEVEL STRING---")
        print("training done.")

    print("\nTRAINING DONE\n")
    print("\n-----!!!NEW PROBLEM!!!-----\n")

    best_individual_index: Tuple[int, int] = max(training_problem.get_best_past_individuals(0))

    print("\nSTART TESTING\n")

    test_problem: KekeProblem = KekeProblem(
        training_batches=[],
        representation=representation,
        max_node_expansions=2000,
        executor=executor,
        test_batch=levels,
        agent_factory=agent_factory
    )
    for _ in measure_time():
        test_problem.register_and_run_next_generation([training_problem.past_instances_by_gen_and_index[best_individual_index]])
