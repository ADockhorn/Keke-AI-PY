
import numpy as np
from pymoo.core.crossover import Crossover
from pymoo.core.duplicate import DuplicateElimination
from pymoo.core.mutation import Mutation
from pymoo.core.problem import Problem
from pymoo.core.sampling import Sampling

from Keke_PY.heuristic_representations.HeuristicRepresentation import HeuristicRepresentation
from Keke_PY.heuristic_representations.TrackedRepresentation import TrackedRepresentation
from Keke_PY.heuristic_representations.WeightedHeuristicSumRepresentation import WeightedHeuristicSumRepresentation
from Keke_PY.heuristics.ParametrisedHeuristic import Heuristic


class DummyRepresentation(HeuristicRepresentation):
    dummy: Heuristic
    _inner_repr: HeuristicRepresentation
    def __init__(
            self,
            dummy: Heuristic,
            inner_representation: HeuristicRepresentation = TrackedRepresentation(WeightedHeuristicSumRepresentation(-1))
    ):
        self.dummy = dummy
        self._inner_repr = inner_representation

    def get_problem_data(self) -> Problem:
        return self._inner_repr.get_problem_data()

    def into_heuristic(self, x: np.ndarray) -> Heuristic:
        return self.dummy
    def serialize(self, x: np.ndarray) -> str:
        return self._inner_repr.serialize(x)
    def deserialize(self, x: str) -> np.ndarray:
        return self._inner_repr.deserialize(x)
    @property
    def sampling(self) -> Sampling:
        return self._inner_repr.sampling
    @property
    def mutation(self) -> Mutation:
        return self._inner_repr.mutation
    @property
    def crossover(self) -> Crossover:
        return self._inner_repr.crossover
    @property
    def duplicate_elimination(self) -> DuplicateElimination:
        return self._inner_repr.duplicate_elimination