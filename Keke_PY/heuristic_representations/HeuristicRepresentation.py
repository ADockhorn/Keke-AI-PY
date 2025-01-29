from abc import ABC, abstractmethod

import numpy as np
from pymoo.core.algorithm import Algorithm
from pymoo.core.crossover import Crossover
from pymoo.core.duplicate import DuplicateElimination
from pymoo.core.mutation import Mutation
from pymoo.core.problem import Problem
from pymoo.core.sampling import Sampling

from Keke_PY.heuristics.ParametrisedHeuristic import Heuristic



class HeuristicRepresentation(ABC):
    @abstractmethod
    def get_problem_data(self) -> Problem:
        pass
    @abstractmethod
    def into_heuristic(self, x: np.ndarray) -> Heuristic:
        pass
    @abstractmethod
    def serialize(self, x: np.ndarray) -> str:
        pass
    @abstractmethod
    def deserialize(self, x: str) -> np.ndarray:
        pass
    @property
    @abstractmethod
    def sampling(self) -> Sampling:
        pass
    @property
    @abstractmethod
    def mutation(self) -> Mutation:
        pass
    @property
    @abstractmethod
    def crossover(self) -> Crossover:
        pass
    @property
    @abstractmethod
    def duplicate_elimination(self) -> DuplicateElimination:
        pass

    def algorithm_arguments(self):
        def get_kwargs(**kwargs):
            return kwargs
        return get_kwargs(
            sampling=self.sampling,
            crossover=self.crossover,
            mutation=self.mutation,
            eliminate_duplicates=self.duplicate_elimination
        )
