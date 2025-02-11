import multiprocessing

import numpy as np

from Keke_PY.experiments.KekeProblem import KekeProblem
from Keke_PY.heuristic_pymoo_representations.DummyRepresentation import DummyRepresentation
from Keke_PY.heuristics.ParametrisedHeuristic import Heuristic


def eval_single_heuristic(heur: Heuristic) -> float:
    representation = DummyRepresentation(heur)
    test_problem = KekeProblem.default_problem(representation, multiprocessing.Pool(20), 3)

    test_problem._evaluate(np.zeros((1, 1), float), )
    pass # TODO?