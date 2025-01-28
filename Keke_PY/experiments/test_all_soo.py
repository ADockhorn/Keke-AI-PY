import multiprocessing
import time
from typing import List, Iterable

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

pop_size: int = 3
n_generations: int = 3
n_evals: int = pop_size * n_generations

#representation = HeuristicTreeRepresentation(3)
representation = WeightedHeuristicSumRepresentation(0.5)
representation = TrackedRepresentation(representation)


optimization_algorithm: Algorithm = [
    RandomSamplingAlgorithm(n_sample_points=n_evals, batch_size=pop_size, sampling=representation.sampling),
    GA(pop_size=pop_size, eliminate_duplicates=True),
    DE(pop_size=pop_size),
    ES(n_offsprings=pop_size, pop_size=pop_size//2),
    PatternSearch(pop_size=pop_size, eliminate_duplicates=True),
][1]

representation.setup(optimization_algorithm)


training_levels = [level["ascii"] for level in load_level_set("./json_levels/train_LEVELS.json")["levels"]][:3]
test_levels = [level["ascii"] for level in load_level_set("./json_levels/test_LEVELS.json")["levels"]][:3]

test_problem = KekeProblem(
    training_batches = [training_levels],
    representation = representation,
    max_forward_model_calls = 2000,
    executor = multiprocessing.Pool(),
    test_batch = test_levels
)

def measure_time() -> Iterable[None]:
    start = time.time()
    yield None
    end = time.time()
    print("The time of execution of above program is :", (end - start), "s")


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
