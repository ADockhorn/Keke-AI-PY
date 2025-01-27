import math
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import TypeVar, Generic, List

import numpy
import numpy as np
from pymoo.core.algorithm import Algorithm
from pymoo.core.crossover import Crossover
from pymoo.core.duplicate import ElementwiseDuplicateElimination, DuplicateElimination
from pymoo.core.individual import Individual
from pymoo.core.mutation import Mutation
from pymoo.core.population import Population
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
    def _sample(self):
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
            xl=None,
            xu=None,
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



class TrackedRepresentation(HeuristicRepresentation):
    _inner_repr: HeuristicRepresentation
    _offset: int
    def __init__(self, inner_representation: HeuristicRepresentation):
        self._inner_repr = inner_representation
        self._offset = 1 + self._inner_repr.crossover.n_parents
    _last_id: int = -1
    def _new_id(self) -> int:
        self._last_id += 1
        return self._last_id
    def register_instance(self, instance: np.ndarray):
        print("TRACKED INSTANCE: ", self.serialize(instance))


    def get_problem_data(self) -> Problem:
        inner_problem_data: Problem = self._inner_repr.get_problem_data()
        return Problem(
            n_var=self._offset + inner_problem_data.n_var,
            xl=(*[-1 for _ in range(self._offset)], *inner_problem_data.xl),
            xu=(*[math.inf for _ in range(self._offset)], *inner_problem_data.xu),
            vtype=inner_problem_data.vtype,
        )

    def into_heuristic(self, x: np.ndarray) -> Heuristic:
        return self._inner_repr.into_heuristic(x[self._offset:])
    def serialize(self, x: np.ndarray) -> str:
        return f"{';'.join(map(str, map(int, x[:self._offset])))};{self._inner_repr.serialize(x[self._offset:])}"
    def deserialize(self, x: str) -> np.ndarray:
        entries = x.split(';')
        track_data: [int] = map(int, entries[:self._offset])
        inner_serialization: str = ';'.join(entries[self._offset:])
        inner_deserialization: [int] = self._inner_repr.deserialize(inner_serialization)
        return np.array([*track_data, *inner_deserialization])
    @property
    def sampling(self) -> Sampling:
        return TrackedRepresentation.TrackedSampling(self)
    @property
    def mutation(self) -> Mutation:
        return TrackedRepresentation.TrackedMutation(self)
    @property
    def crossover(self) -> Crossover:
        return TrackedRepresentation.TrackedCrossover(self)
    @property
    def duplicate_elimination(self) -> DuplicateElimination:
        return TrackedRepresentation.TrackedDuplicateElimination(self)


    def _get_inner_problem(self, problem: Problem) -> Problem:
        return Problem(
            n_var=problem.n_var - self._offset,
            n_obj=problem.n_obj,
            n_ieq_constr=problem.n_ieq_constr,
            n_eq_constr=problem.n_eq_constr,
            xl=problem.xl[self._offset:],
            xu=problem.xu[self._offset:],
            vtype=problem.vtype,
        )

    class TrackedSampling(Sampling):
        _tracked_repr: 'TrackedRepresentation'
        _inner_sampling: Sampling
        def __init__(self, tracked_representation: 'TrackedRepresentation'):
            self._tracked_repr = tracked_representation
            self._inner_sampling = tracked_representation._inner_repr.sampling
            super().__init__()
        def _do(self, problem, n_samples, **kwargs) -> np.ndarray:
            inner = self._inner_sampling._do(self._tracked_repr._get_inner_problem(problem), n_samples, **kwargs)
            res = numpy.pad(inner, ((0, 0), (self._tracked_repr._offset, 0)), constant_values=-1)
            for i in range(n_samples):
                res[i, 0] = self._tracked_repr._new_id()
                self._tracked_repr.register_instance(deepcopy(res[i, :]))
            return res

    class TrackedMutation(Mutation):
        _tracked_repr: 'TrackedRepresentation'
        _inner_mutation: Mutation
        def __init__(self, tracked_representation: 'TrackedRepresentation'):
            self._tracked_repr = tracked_representation
            self._inner_mutation = tracked_representation._inner_repr.mutation
            super().__init__()
        def _do(self, problem, x, **kwargs):
            inner_x: np.ndarray = x[:, self._tracked_repr._offset:]
            inner_res: np.ndarray = self._inner_mutation._do(self._tracked_repr._get_inner_problem(problem), inner_x, **kwargs)
            res: np.ndarray = x if id(inner_res) == id(inner_x) else \
                numpy.pad(inner_res, ((0, 0), (self._tracked_repr._offset, 0)), constant_values=-1)
            for i in range(len(x)):
                res[i, 1:self._tracked_repr._offset] = -1
                res[i, 1] = x[i, 0]
                res[i, 0] = self._tracked_repr._new_id()
                self._tracked_repr.register_instance(deepcopy(res[i, :]))
            return res

    class TrackedCrossover(Crossover):
        _tracked_repr: 'TrackedRepresentation'
        _inner_crossover: Crossover

        def __init__(self, tracked_representation: 'TrackedRepresentation'):
            self._tracked_repr = tracked_representation
            self._inner_crossover = tracked_representation._inner_repr.crossover
            super().__init__(
                self._inner_crossover.n_parents,
                self._inner_crossover.n_offsprings,
                self._inner_crossover.prob,
            )

        def do(self, problem, pop, parents=None, **kwargs):
            prob_src = self.prob
            self.prob = prob_src.get()
            result = Crossover.do(self, problem, pop, parents, **kwargs)
            self.prob = prob_src
            return result

        def _do(self, problem, x, **kwargs):
            inner_x = x[:, :, self._tracked_repr._offset:]
            inner_res = self._inner_crossover._do(self._tracked_repr._get_inner_problem(problem), inner_x, **kwargs)
            res = numpy.pad(inner_res, ((0, 0), (0, 0), (self._tracked_repr._offset, 0)), constant_values=-1)
            # The inner result has the following shape (n_offspring, n_matings, n_var)
            n_offsprings, n_matings, _ = res.shape
            for i in range(n_matings):
                parents = x[:, i, 0]
                for j in range(n_offsprings):
                    res[j, i, 0] = self._tracked_repr._new_id()
                    res[j, i, 1:1+self._inner_crossover.n_parents] = parents
                    self._tracked_repr.register_instance(deepcopy(res[j, i, :]))
            return res

    class TrackedDuplicateElimination(DuplicateElimination):
        _tracked_repr: 'TrackedRepresentation'
        _inner_duplicate_elimination: DuplicateElimination
        def __init__(self, tracked_representation: 'TrackedRepresentation'):
            self._tracked_repr = tracked_representation
            self._inner_duplicate_elimination = tracked_representation._inner_repr.duplicate_elimination
            super().__init__()

        def _do(self, pop, other, is_duplicate):
            def inner_individual(individual: Individual) -> Individual:
                res = individual.copy()
                res.X = individual.X[self._tracked_repr._offset:]
                return res
            def inner_population(p: Population) -> Population:
                return Population(list(map(inner_individual, p)))
            inner_pop = inner_population(pop)
            inner_other = None if other is None else inner_population(other)
            self._inner_duplicate_elimination._do(inner_pop, inner_other, is_duplicate)
            return is_duplicate