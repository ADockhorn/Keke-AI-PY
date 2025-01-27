from copy import deepcopy
from typing import List

import numpy as np
from pymoo.core.crossover import Crossover
from pymoo.core.duplicate import DuplicateElimination, DefaultDuplicateElimination
from pymoo.core.mutation import Mutation
from pymoo.core.problem import Problem
from pymoo.core.sampling import Sampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM

from Keke_PY.baba import GameState
from Keke_PY.heuristics.HeuristicRepresentation import HeuristicRepresentation
from Keke_PY.heuristics.ParametrisedHeuristic import Heuristic
from Keke_PY.heuristics.hand_crafted_heuristics import heuristics, heuristics_feature_vector_length


class WeightedHeuristicSum(Heuristic):

    weights: List[float]
    do_nothing_threshold: float

    def __init__(self, weights: List[float], do_nothing_threshold: float = 0.01):
        assert len(weights) == heuristics_feature_vector_length
        self.weights = deepcopy(list(weights))
        self.do_nothing_threshold = do_nothing_threshold


    def run(self, state: GameState, ctx: dict, *args: float) -> float:
        feature_sum: float = 0.0
        weights_read_index: int = 0
        for heuristic in heuristics:
            weight: float = self.weights[weights_read_index]
            weights_read_index += 1
            if abs(weight) <= self.do_nothing_threshold:
                weights_read_index += heuristic.nr_of_parameters
            else:
                additional_parameters: List[float] = self.weights[
                    weights_read_index : weights_read_index + heuristic.nr_of_parameters
                ]
                weights_read_index += heuristic.nr_of_parameters
                feature_sum += weight * heuristic.run(state, ctx, *additional_parameters)
        return feature_sum


class WeightedHeuristicSumRepresentation(HeuristicRepresentation):

    do_nothing_threshold: float
    def __init__(self, do_nothing_threshold: float = 0.01):
        self.do_nothing_threshold = do_nothing_threshold

    def get_problem_data(self) -> Problem:
        return Problem(
            n_var=heuristics_feature_vector_length,
            xl=-10.0,
            xu=10.0,
            vtype=float,
        )

    def into_heuristic(self, x: np.ndarray) -> Heuristic:
        return WeightedHeuristicSum(list(x), self.do_nothing_threshold)

    def serialize(self, x: np.ndarray) -> str:
        return ';'.join(map(str, x))

    def deserialize(self, x: str) -> np.ndarray:
        return np.fromiter(map(float, x.split(';')), float)

    @property
    def sampling(self) -> Sampling:
        return WeightedHeuristicSumRepresentation.FloatRandomSampling()
    @property
    def mutation(self) -> Mutation:
        return PM()
    @property
    def crossover(self) -> Crossover:
        return SBX()
    @property
    def duplicate_elimination(self) -> DuplicateElimination:
        return DefaultDuplicateElimination()

    class FloatRandomSampling(Sampling):
        xl: float = -10.0
        xu: float = 10.0

        def _do(self, problem, n_samples, **kwargs):
            x = np.random.random((n_samples, heuristics_feature_vector_length))
            x = self.xl + (self.xu - self.xl) * x

            return x