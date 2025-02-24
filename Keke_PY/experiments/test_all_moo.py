import multiprocessing
from typing import List

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize

from Keke_PY.heuristic_pymoo_representations.WeightedHeuristicSumRepresentation import WeightedHeuristicSumRepresentation
from Keke_PY.experiments.KekeProblem import KekeProblem
from Keke_PY.keke_game.simulation import load_level_set

pop_size = 3# 10
n_generations = 3# 20
#levels_per_objective = 25
optimization_algorithm = NSGA2(pop_size=pop_size)
#problem = MultiObjectiveKeke(results_dict=results_dict, levels_per_objective=levels_per_objective)

#pop_size = 10
#n_generations = 20
#levels_per_objective = 10
#optimization_algorithm = NSGA2(pop_size=pop_size)
#problem = MultiObjectiveKeke(results_dict=results_dict, levels_per_objective=levels_per_objective)

#pop_size = 10
#n_generations = 20
#levels_per_objective = 5
#optimization_algorithm = NSGA2(pop_size=pop_size)
#problem = MultiObjectiveKeke(results_dict=results_dict, levels_per_objective=levels_per_objective)


# NSGA 3 (each setup is overwriting population size and generations to ensure the same number of evaluations)

#pop_size = 10
#n_generations = 20
#levels_per_objective = 25
#ref_dirs = get_reference_directions("das-dennis", 2, n_partitions=4)
#optimization_algorithm = NSGA3(pop_size=10, ref_dirs=ref_dirs)


#pop_size = 20
#n_generations = 10
#levels_per_objective = 10
#ref_dirs = get_reference_directions("das-dennis", 5, n_partitions=12)
#optimization_algorithm = NSGA3(pop_size=pop_size, ref_dirs=ref_dirs)


level_set = load_level_set("./json_levels/train_LEVELS.json")
test_batch: List[str] = [level_set["levels"][index]["ascii"] for index in range(50)][:3]

test_problem = KekeProblem([test_batch], WeightedHeuristicSumRepresentation(), 2000, multiprocessing.Pool())



if __name__ == '__main__':

    print(f"testing {optimization_algorithm} ...")


    res = minimize(
        test_problem,
        optimization_algorithm,
        termination=("n_gen", n_generations),
    )


    print(f"testing {optimization_algorithm} done")
