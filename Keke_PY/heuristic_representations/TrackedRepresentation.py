import math
from copy import deepcopy
from typing import List

import numpy
import numpy as np
from pymoo.core.crossover import Crossover
from pymoo.core.duplicate import DuplicateElimination
from pymoo.core.individual import Individual
from pymoo.core.mutation import Mutation
from pymoo.core.population import Population
from pymoo.core.problem import Problem
from pymoo.core.sampling import Sampling

from Keke_PY.heuristic_representations.HeuristicRepresentation import HeuristicRepresentation
from Keke_PY.heuristics.ParametrisedHeuristic import Heuristic


class TrackedRepresentation(HeuristicRepresentation):
    _inner_repr: HeuristicRepresentation
    _offset: int
    def __init__(self, inner_representation: HeuristicRepresentation):
        self._inner_repr = inner_representation
        self._offset = 1 + self._inner_repr.crossover.n_parents
    _tracked_instances: List[np.ndarray] = []
    def _current_id(self) -> int:
        return len(self._tracked_instances)
    def track_instance(self, problem, instance: np.ndarray):
        assert instance[0] == len(self._tracked_instances), "instance must have id equal to _current_id()"
        self._tracked_instances.append(instance.copy())
        problem.log_text(f"TRACK: {self.serialize(instance, False)}")



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
    def serialize(self, x: np.ndarray, just_id: bool = True) -> str:
        if just_id:
            return str(int(x[0]))
        return f"{';'.join(map(str, map(int, x[:self._offset])))};{self._inner_repr.serialize(x[self._offset:])}"
    def deserialize(self, x: str, just_id: bool = True) -> np.ndarray:
        if just_id:
            return self._tracked_instances[int(x)]
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
                res[i, 0] = self._tracked_repr._current_id()
                self._tracked_repr.track_instance(problem, deepcopy(res[i, :]))
            return res

    class TrackedMutation(Mutation):
        _tracked_repr: 'TrackedRepresentation'
        _inner_mutation: Mutation

        def __init__(self, tracked_representation: 'TrackedRepresentation'):
            self._tracked_repr = tracked_representation
            self._inner_mutation = tracked_representation._inner_repr.mutation
            super().__init__()
            self.prob = self._inner_mutation.prob.get()

        def do(self, problem, pop, inplace=True, **kwargs):
            self.prob = self._inner_mutation.prob.get()
            return Mutation.do(self, problem, pop, inplace, **kwargs)

        def _do(self, problem, x, **kwargs):
            inner_x: np.ndarray = x[:, self._tracked_repr._offset:]
            inner_res: np.ndarray = self._inner_mutation._do(self._tracked_repr._get_inner_problem(problem), inner_x, **kwargs)
            res: np.ndarray = x if id(inner_res) == id(inner_x) else \
                numpy.pad(inner_res, ((0, 0), (self._tracked_repr._offset, 0)), constant_values=-1)
            for i in range(len(x)):
                res[i, 1:self._tracked_repr._offset] = -1
                res[i, 1] = x[i, 0]
                res[i, 0] = self._tracked_repr._current_id()
                self._tracked_repr.track_instance(problem, deepcopy(res[i, :]))
            return res

    class TrackedCrossover(Crossover):
        _tracked_repr: 'TrackedRepresentation'
        _inner_crossover: Crossover

        def __init__(self, tracked_representation: 'TrackedRepresentation'):
            self._tracked_repr = tracked_representation
            self._inner_crossover = tracked_representation._inner_repr.crossover
            super().__init__(
                self._inner_crossover.n_parents,
                self._inner_crossover.n_offsprings
            )
            self.prob = self._inner_crossover.prob.get()

        def do(self, problem, pop, parents=None, **kwargs):
            self.prob = self._inner_crossover.prob.get()
            return Crossover.do(self, problem, pop, parents, **kwargs)

        def _do(self, problem, x, **kwargs):
            inner_x = x[:, :, self._tracked_repr._offset:]
            inner_res = self._inner_crossover._do(self._tracked_repr._get_inner_problem(problem), inner_x, **kwargs)
            res = numpy.pad(inner_res, ((0, 0), (0, 0), (self._tracked_repr._offset, 0)), constant_values=-1)
            # The inner result has the following shape (n_offspring, n_matings, n_var)
            n_offsprings, n_matings, _ = res.shape
            for i in range(n_matings):
                parents = x[:, i, 0]
                for j in range(n_offsprings):
                    res[j, i, 0] = self._tracked_repr._current_id()
                    res[j, i, 1:1+self._inner_crossover.n_parents] = parents
                    self._tracked_repr.track_instance(problem, deepcopy(res[j, i, :]))
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
