import multiprocessing
from typing import Tuple, Dict

import numpy as np

from Keke_PY.experiments.KekeProblem import KekeProblem
from Keke_PY.heuristic_pymoo_representations.DummyRepresentation import DummyRepresentation
from Keke_PY.heuristics.ParametrisedHeuristic import Heuristic
from Keke_PY.heuristics.ZeroHeuristic import ZeroHeuristic
from Keke_PY.search_agents.AStar import AStar


def eval_single_heuristic(heur: Heuristic) -> Dict[int, float]:
    representation = DummyRepresentation(heur)
    test_problem = KekeProblem.default_problem(representation, multiprocessing.Pool())

    performance_of_instance_on_batch: Dict[Tuple[int, int], float] = test_problem.evaluate_performance_of_instance_on_batch([AStar(heur)])

    performances: Dict[int, float] = dict((key[1], value) for key, value in performance_of_instance_on_batch.items())

    print(performances)
    return performances

if __name__ == "__main__":

    eval_single_heuristic(ZeroHeuristic())
