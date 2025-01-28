from pymoo.algorithms.hyperparameters import SingleObjectiveSingleRun, HyperparameterProblem
from pymoo.algorithms.soo.nonconvex.optuna import Optuna
from pymoo.core.parameters import set_params, hierarchical
from pymoo.optimize import minimize

from Keke_PY.experiments.test_all_soo import optimization_algorithm, test_problem

if __name__ == '__main__':

    print(f"testing {optimization_algorithm} ...")
    dump_file_name: str = "test_1_return.pickle"

    performance = SingleObjectiveSingleRun(test_problem, termination=("n_evals", 10))

    res = minimize(HyperparameterProblem(optimization_algorithm, performance),
                   Optuna(),
                   termination=('n_evals', 5),
                   seed=1,
                   verbose=False)
    print(res.X)

    set_params(optimization_algorithm, hierarchical(res.X))

    res = minimize(
        test_problem,
        optimization_algorithm,
        termination=("n_eval", 10),
        verbose=True
    )


    print(f"testing {optimization_algorithm} done")