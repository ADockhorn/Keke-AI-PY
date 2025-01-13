import multiprocessing
import pickle

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize

from Keke_PY.heuristic_training.HeuristicTreeProblem import HeuristicTreeProblem, TrainingRecord
from Keke_PY.heuristic_training.test_training import test_batches
from Keke_PY.heuristics.HeuristicTree import HeuristicTree

test_problem = HeuristicTreeProblem(2, test_batches, 2000, multiprocessing.Pool())

optimization_algorithm = NSGA2(
    pop_size = 3,
    sampling = HeuristicTree.Sampling(),
    crossover = HeuristicTree.Crossover(),
    mutation = HeuristicTree.Mutation(),
    eliminate_duplicates = HeuristicTree.DuplicationElimination()
)






if __name__ == '__main__':

    dump_file_name: str = "tree_test_return.pickle"

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

    print(pickle.dumps())