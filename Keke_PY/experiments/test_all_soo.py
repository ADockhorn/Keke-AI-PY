from math import floor

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
from Keke_PY.heuristic_representations.HeuristicTreeRepresentation import HeuristicTreeRepresentation
from Keke_PY.heuristic_representations.TrackedRepresentation import TrackedRepresentation
from Keke_PY.heuristic_representations.WeightedHeuristicSumRepresentation import WeightedHeuristicSumRepresentation
from Keke_PY.simulation import load_level_set

setups: [(bool, bool, int)] = (
    (False, True, 0),
    (False, True, 1),
    (False, False, 2),
    (False, False, 3),
    (False, False, 4),
    (True, True, 0),
    (True, True, 1),
)
trees, track, algorithm = setups[1 if len(sys.argv) != 2 else int(sys.argv[1])]

pop_size: int = 1#3
n_generations: int = 1#3


n_evals: int = pop_size * n_generations

representation = HeuristicTreeRepresentation(10) if trees else WeightedHeuristicSumRepresentation(-1)#0.5)
if track:
    representation = TrackedRepresentation(representation)


optimization_algorithm: Algorithm = [
    RandomSamplingAlgorithm(n_sample_points=n_evals, batch_size=pop_size, **representation.algorithm_arguments()),
    GA(pop_size=pop_size, **representation.algorithm_arguments()),
    DE(pop_size=pop_size),
    ES(n_offsprings=pop_size, pop_size=pop_size//2),
    PatternSearch(pop_size=pop_size, eliminate_duplicates=True), #TODO@ask: pop_size doesn't have any effect
][algorithm]

levels: List[str] = [
    *[level["ascii"] for level in load_level_set("./json_levels/train_LEVELS.json")["levels"]],
    *[level["ascii"] for level in load_level_set("./json_levels/test_LEVELS.json")["levels"]],
][:20]
training_ratio: float = 0.6
training_levels: List[str] = levels[:floor(training_ratio * len(levels))]
test_levels: List[str] = levels[floor(training_ratio * len(levels)):]

test_problem = KekeProblem(
    training_batches = [training_levels],
    representation = representation,
    max_forward_model_calls = 2000,
    executor = multiprocessing.Pool(2),
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
        dump_file_name: str = "test_1_return.pickle"



        res = minimize(
            test_problem,
            optimization_algorithm,
            termination=("n_eval", n_evals),
            verbose=True
        )


        print(f"testing {optimization_algorithm} done")


# Time t of one evaluation of one individual with multiprocessing.Pool(x) executor on my laptop:
# Time t' is the time on 20cpus when perfect parallelization is assumed

# x = 1: t = 1853.0943999290466 s => t' = 1854s * 200 * 1cpus / 20cpus = 18540s = 309min = 5.15h
# x = 2: t =
# x = 4: t = 630.5655705928802 s => t' = 630s * 200 * 4cpus / 20cpus = 25200s = 420min = 7h
# x = 8: t = 564.6523087024689 s => t' = 570s * 200 * 8cpus / 20cpus = 45600s = 760min <= 13h
# x = 8: t = 431.1010444164276 s => t' = 431s * 200 * 8cpus / 20cpus = 34480s = 575min <= 10h (with a good individual)



# Time t of one evaluation of one individual with multiprocessing.ProcessPoolExecutor(x) executor on my laptop:
# Time t' is the time on 20cpus when perfect parallelization is assumed
# x = 8: t = 424.2974717617035 s => t' = 424s * 200 * 8cpus / 20cpus = 33920s = 565min <= 9.5h (with a good individual)


# multiprocessing.ThreadPoolExecutor(x) never finished


# TODO: check, if the suboptimal cpu usage is due to my laptop or the program!