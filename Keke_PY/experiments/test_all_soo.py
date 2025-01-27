import multiprocessing
from typing import List

from pymoo.algorithms.soo.nonconvex.de import DE
from pymoo.algorithms.soo.nonconvex.es import ES
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.algorithms.soo.nonconvex.pattern import PatternSearch
from pymoo.core.algorithm import Algorithm
from pymoo.optimize import minimize

from Keke_PY.heuristic_training.KekeProblem import KekeProblem
from Keke_PY.heuristic_training.LinearHeuristicCombinationProblem import TrainingRecord
from Keke_PY.heuristic_representations.TrackedRepresentation import TrackedRepresentation
from Keke_PY.heuristic_representations.WeightedHeuristicSumRepresentation import WeightedHeuristicSumRepresentation
from Keke_PY.simulation import load_level_set

pop_size: int = 3
n_generations: int = 3

#representation = HeuristicTree
representation = WeightedHeuristicSumRepresentation()
representation = TrackedRepresentation(representation)


optimization_algorithm: Algorithm = [
    GA(pop_size=pop_size, eliminate_duplicates=True),
    DE(pop_size=pop_size),
    ES(n_offsprings=pop_size, pop_size=pop_size//2),     # gives it 5 more evaluations than other algorithms TODO@ask: ???
    PatternSearch(pop_size=pop_size, eliminate_duplicates=True),
][0]

representation.setup(optimization_algorithm)


level_set = load_level_set("./json_levels/train_LEVELS.json")
levels: List[str] = [level_set["levels"][index]["ascii"] for index in range(50)]
training_batches: List[List[str]] = [levels[:1]]
test_batch: [str] = levels[1:2]

test_problem = KekeProblem(
    training_batches = training_batches,
    representation = representation,
    max_forward_model_calls = 2000,
    executor = multiprocessing.Pool(),
    test_batch = test_batch
)



if __name__ == '__main__':

    print(f"testing {optimization_algorithm} ...")
    dump_file_name: str = "test_1_return.pickle"

    callback = TrainingRecord()


    res = minimize(
        test_problem,
        optimization_algorithm,
        termination=("n_gen", n_generations),
        callback=callback,
        verbose=True
    )


    print(f"testing {optimization_algorithm} done")
