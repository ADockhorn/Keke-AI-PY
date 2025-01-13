import multiprocessing
import pickle
from typing import List, Tuple, Union, Iterable

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize

from Keke_PY.heuristic_training.LinearHeuristicCombinationProblem import LinearHeuristicCombinationProblem, \
    TrainingRecord
from Keke_PY.simulation import load_level_set


test_files_as_batches: List[Tuple[str, Union[range, int, None, Iterable[int]]]] = [
    (
        "./json_levels/demo_LEVELS.json",
        [i for i in range(14) if i not in range(1, 1000)]
    ), (
        "./json_levels/test_LEVELS.json",
        [i for i in range(0, 134) if i not in range(1, 1000)]
    )
]

test_batches: List[List[str]] = []

for file_name, level_nrs in test_files_as_batches:
    batch: List[str] = []
    level_set = load_level_set(file_name)
    if level_nrs is None:
        level_nrs = range(len(level_set["levels"]))
    if level_nrs.__class__ == int:
        level_nrs = range(level_nrs, level_nrs + 1)
    for index in level_nrs:
        demo_level: str = level_set["levels"][index]["ascii"]
        batch.append(demo_level)
    test_batches.append(batch)

test_problem = LinearHeuristicCombinationProblem(test_batches, 2000, multiprocessing.Pool())

optimization_algorithm = NSGA2(pop_size=3)






if __name__ == '__main__':

    dump_file_name: str = "test_return.pickle"

    callback = TrainingRecord()

    res = minimize(
        test_problem,
        optimization_algorithm,
        termination=("n_gen", 3),
        callback=callback
    )

    with open(dump_file_name, "wb") as file:
        pickle.dump(callback, file)

    with open(dump_file_name, "rb") as file:
        loaded_data = pickle.load(file)

    print(loaded_data.__class__)
