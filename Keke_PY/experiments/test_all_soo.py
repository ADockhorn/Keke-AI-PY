import multiprocessing
from typing import List

from pymoo.algorithms.soo.nonconvex.de import DE
from pymoo.algorithms.soo.nonconvex.es import ES
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.algorithms.soo.nonconvex.pattern import PatternSearch
from pymoo.core.algorithm import Algorithm
from pymoo.optimize import minimize

from Keke_PY.heuristic_training.LinearHeuristicCombinationProblem import TrainingRecord, \
    LinearHeuristicCombinationProblem
from Keke_PY.simulation import load_level_set

pop_size: int = 3
n_generations: int = 3

optimization_algorithm: Algorithm = [
    GA(pop_size=pop_size, eliminate_duplicates=True),
    DE(pop_size=pop_size),
    ES(n_offsprings=pop_size, pop_size=pop_size//2),     # gives it 5 more evaluations than other algorithms TODO@ask: ???
    PatternSearch(pop_size=pop_size, eliminate_duplicates=True),
][0]


level_set = load_level_set("./json_levels/train_LEVELS.json")
test_batch: List[str] = [level_set["levels"][index]["ascii"] for index in range(50)]#[:3]

test_problem = LinearHeuristicCombinationProblem([test_batch], 2000, multiprocessing.Pool())




if __name__ == '__main__':

    print(f"testing {optimization_algorithm} ...")
    dump_file_name: str = "test_1_return.pickle"

    callback = TrainingRecord()

    res = minimize(
        test_problem,
        optimization_algorithm,
        termination=("n_gen", n_generations),
        callback=callback
    )


    print(f"testing {optimization_algorithm} done")
