from abc import ABC, abstractmethod

import numpy as np
from pymoo.core.algorithm import Algorithm
from pymoo.core.crossover import Crossover
from pymoo.core.duplicate import DuplicateElimination, NoDuplicateElimination
from pymoo.core.mutation import Mutation
from pymoo.core.problem import Problem
from pymoo.core.sampling import Sampling
from pymoo.operators.mutation.nom import NoMutation

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


    def setup(self, alg: Algorithm):
        sampling, crossover, mutation, duplicate_elimination = (
            self.sampling, self.crossover, self.mutation, self.duplicate_elimination
        )
        alg.eliminate_duplicates = duplicate_elimination
        #if alg.initialization is not None:
        alg.initialization.sampling = sampling
        alg.initialization.eliminate_duplicates = duplicate_elimination
        alg.mating.eliminate_duplicates = duplicate_elimination
        alg.mating.crossover = crossover
        alg.mating.mutation = mutation

