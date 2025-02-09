if True:
    """Include Project root as Environment paths:"""
    from os.path import dirname, abspath
    import sys
    sys.path.append(dirname(dirname(dirname(abspath(__file__)))))

import os
from math import floor

from Keke_PY.heuristic_representations.DummyRepresentation import DummyRepresentation
from Keke_PY.heuristics.WeightedHeuristicSum import WeightedHeuristicSum
from Keke_PY.heuristics.hand_crafted_heuristics import heuristics_feature_vector_length

import multiprocessing
import time
from typing import Iterable, List

from pymoo.core.algorithm import Algorithm
from pymoo.optimize import minimize

from Keke_PY.experiments.RandomSamplingAlgorithm import RandomSamplingAlgorithm
from Keke_PY.experiments.KekeProblem import KekeProblem
from Keke_PY.simulation import load_level_set



representation = DummyRepresentation(WeightedHeuristicSum(
    [0.0] * heuristics_feature_vector_length, -1
))

optimization_algorithm: Algorithm = RandomSamplingAlgorithm(n_sample_points=1, batch_size=1, **representation.algorithm_arguments())

levels: List[str] = [
    *[level["ascii"] for level in load_level_set("./json_levels/train_LEVELS.json")["levels"]],
    *[level["ascii"] for level in load_level_set("./json_levels/test_LEVELS.json")["levels"]],
]
training_ratio: float = 0.6
training_levels: List[str] = levels[:floor(training_ratio * len(levels))]
test_levels: List[str] = levels[floor(training_ratio * len(levels)):]

print("Reported CPU counts:", multiprocessing.cpu_count(), os.cpu_count())
processes = multiprocessing.cpu_count() if len(sys.argv) != 2 else int(sys.argv[1])
print("Requesting", processes, "processes")


test_problem = KekeProblem(
    training_batches = [training_levels],
    representation = representation,
    max_forward_model_calls = 2000,
    executor = multiprocessing.Pool(processes=processes),
    test_batch = test_levels
)

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
            termination=("n_eval", 1),
            verbose=True
        )


        print(f"testing {optimization_algorithm} done")


# Runtimes on my laptop:
# processes=8 => 518.1460421085358 s
# processes=4 => 587.7105324268341 s