import math
from abc import abstractmethod
from typing import Generic, TypeVar

import numpy as np
from pymoo.core.crossover import Crossover
from pymoo.core.duplicate import DuplicateElimination, ElementwiseDuplicateElimination
from pymoo.core.mutation import Mutation
from pymoo.core.problem import Problem
from pymoo.core.sampling import Sampling

from Keke_PY.heuristic_pymoo_representations.HeuristicRepresentation import HeuristicRepresentation
from Keke_PY.heuristics.ParametrisedHeuristic import Heuristic



T = TypeVar('T', bound=np.generic)

class SingleObjRepresentation(Generic[T], HeuristicRepresentation):

    @abstractmethod
    def _assert_type(self, x: object) -> T:
        pass
    @abstractmethod
    def _into_heuristic(self, x: T) -> Heuristic:
        pass
    @abstractmethod
    def _serialize(self, x: T) -> str:
        pass
    @abstractmethod
    def _deserialize(self, x: str) -> T:
        pass
    @abstractmethod
    def _sample(self) -> T:
        pass
    @abstractmethod
    def _mutate(self, x: T) -> T:
        pass
    @abstractmethod
    def _crossover(self, x: T, y: T) -> T:
        pass
    @abstractmethod
    def _are_equal(self, x: T, y: T) -> bool:
        pass

    def get_problem_data(self) -> Problem:
        return Problem(
            n_var=1,
            xl=(-math.inf,),
            xu=(math.inf,),
            vtype=object,
        )
    def into_heuristic(self, x: np.ndarray) -> Heuristic:
        return self._into_heuristic(self._assert_type(x[0]))
    def serialize(self, x: np.ndarray) -> str:
        return self._serialize(self._assert_type(x[0]))
    def deserialize(self, x: str) -> np.ndarray:
        return np.array(self._deserialize(x))

    @property
    def sampling(self) -> Sampling:
        return SingleObjRepresentation.Sampling[T](self)
    @property
    def mutation(self) -> Mutation:
        return SingleObjRepresentation.Mutation[T](self)
    @property
    def crossover(self) -> Crossover:
        return SingleObjRepresentation.Crossover[T](self)
    @property
    def duplicate_elimination(self) -> DuplicateElimination:
        return SingleObjRepresentation.DuplicateElimination[T](self)

    class Sampling(Sampling, Generic[T]):
        representation: 'SingleObjRepresentation[T]'

        def __init__(self, representation: 'SingleObjRepresentation[T]'):
            super().__init__()
            self.representation = representation

        def _do(self, problem, n_samples, **kwargs):
            res = np.full((n_samples, 1), None, dtype=object)
            for i in range(n_samples):
                res[i, 0] = self.representation._sample()
            return res

    class Mutation(Mutation, Generic[T]):
        representation: 'SingleObjRepresentation[T]'

        def __init__(self, representation: 'SingleObjRepresentation[T]'):
            super().__init__()
            self.representation = representation

        def _do(self, problem, x, **kwargs):
            # for each individual
            for i in range(len(x)):
                x[i, 0] = self.representation._mutate(x[i, 0])
            return x

    class Crossover(Crossover, Generic[T]):
        representation: 'SingleObjRepresentation[T]'

        def __init__(self, representation: 'SingleObjRepresentation[T]'):
            super().__init__(2, 2)
            self.representation = representation

        def _do(self, problem, x, **kwargs):
            # The input of has the following shape (n_parents, n_matings, n_var)
            _, n_matings, n_var = x.shape
            # The output with the shape (n_offsprings, n_matings, n_var)
            # Because there the number of parents and offsprings are equal it keeps the shape of x
            res = np.full_like(x, None, dtype=object)
            # for each mating provided
            for k in range(n_matings):
                # get the first and the second parent
                parent1, parent2 = x[0, k, 0], x[1, k, 0]
                offspring1 = self.representation._crossover(parent1, parent2)
                offspring2 = self.representation._crossover(parent2, parent1)
                res[0, k, 0], res[1, k, 0] = offspring1, offspring2
            return res

    class DuplicateElimination(ElementwiseDuplicateElimination, Generic[T]):
        representation: 'SingleObjRepresentation[T]'

        def __init__(self, representation: 'SingleObjRepresentation[T]'):
            super().__init__()
            self.representation = representation

        def is_equal(self, a, b):
            return self.representation._are_equal(a.X[0], b.X[0])
