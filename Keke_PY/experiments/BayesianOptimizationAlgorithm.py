from typing import Optional, Tuple, Dict

import numpy as np
from bayes_opt import BayesianOptimization, UtilityFunction
from pymoo.core.algorithm import LoopwiseAlgorithm
from pymoo.core.population import Population
from pymoo.core.problem import Problem


class BayesianOptimizationAlgorithm(LoopwiseAlgorithm):

    utility_function: UtilityFunction = UtilityFunction()
    optimizer: Optional[BayesianOptimization] = None
    remaining_evals: int
    def __init__(self, initial_remaining_evals: int, **kwargs):
        super().__init__(**kwargs)
        self.remaining_evals = initial_remaining_evals

    def get_optimizer(self, problem: Problem = None) -> BayesianOptimization:
        if problem is None:
            problem = self.problem
        if self.optimizer is None:
            n_var: int = problem.n_var
            pymoo_bounds: Tuple[np.ndarray, np.ndarray] = problem.bounds()
            bayes_bounds: Dict[str, Tuple[float, float]] = dict(
                (str(index), (float(pymoo_bounds[0][index]), float(pymoo_bounds[1][index])))
                for index in range(n_var)
            )
            self.optimizer = BayesianOptimization(
                f=None,
                pbounds=bayes_bounds,
            )
        return self.optimizer

    def get_optimizer_suggestion(self) -> np.ndarray:
        optimizer = self.get_optimizer()
        bayes_sug = optimizer.suggest(self.utility_function)
        sug_buffer = np.fromiter((bayes_sug[str(index)] for index in range(self.problem.n_var)), float)
        return sug_buffer

    def register_evaluation(self, x: np.ndarray, f: float):
        optimizer = self.get_optimizer()
        bayes_x = dict((str(index), x[index]) for index in range(self.problem.n_var))
        optimizer.register(bayes_x, -f)

    def _next(self):
        return self

    def send(self, _infill):
        if self.remaining_evals <= 0:
            raise StopIteration()
        self.remaining_evals -= 1
        if _infill is not None:
            for individual in _infill:
                self.register_evaluation(individual.X, float(individual.F))
        pymoo_buffer = np.zeros((1, self.problem.n_var))
        pymoo_buffer[0,:] = self.get_optimizer_suggestion()[:]
        pymoo_res = Population.new("X", pymoo_buffer)
        return pymoo_res