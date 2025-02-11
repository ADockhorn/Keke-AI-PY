
import numpy as np
from pymoo.core.crossover import Crossover
from pymoo.core.duplicate import DuplicateElimination
from pymoo.core.mutation import Mutation
from pymoo.core.problem import Problem
from pymoo.core.sampling import Sampling

from Keke_PY.heuristic_pymoo_representations.HeuristicRepresentation import HeuristicRepresentation
from Keke_PY.heuristic_pymoo_representations.SingleObjRepresentation import SingleObjRepresentation
from Keke_PY.heuristics.ParametrisedHeuristic import Heuristic
from Keke_PY.heuristics.SimpleHeuristic import SimpleHeuristic
from Keke_PY.heuristics.ZeroHeuristic import ZeroHeuristic


class DummyRepresentation(HeuristicRepresentation):
    dummy: Heuristic
    _inner_repr: HeuristicRepresentation
    def __init__(
            self,
            dummy: Heuristic = SimpleHeuristic(),
            inner_representation: HeuristicRepresentation = None
    ):
        if inner_representation is None:
            inner_representation = ZeroHeuristicRepresentation()
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

class ZeroHeuristicRepresentation(SingleObjRepresentation[int]):
    def _assert_type(self, x: object) -> int:
        assert isinstance(x, int)
        return x

    def _into_heuristic(self, x: int) -> Heuristic:
        return ZeroHeuristic()

    def _serialize(self, x: int) -> str:
        return '_'

    def _deserialize(self, x: str) -> int:
        return 0

    def _sample(self) -> int:
        return 0

    def _mutate(self, x: int) -> int:
        return 0

    def _crossover(self, x: int, y: int) -> int:
        return 0

    def _are_equal(self, x: int, y: int) -> bool:
        return False