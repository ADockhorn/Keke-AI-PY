import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from inspect import signature
from typing import Callable, List

from Keke_PY.baba import GameState
from Keke_PY.heuristics.ParametrisedHeuristic import ParametrisedHeuristic, ParametrisedHeuristicFromCallable


class HeuristicCombinator(ParametrisedHeuristic, ABC):

    @property
    @abstractmethod
    def nr_of_static_parameters(self) -> int:
        pass

    @property
    def nr_of_dynamic_inputs(self) -> int:
        return self.nr_of_parameters - self.nr_of_static_parameters

    @staticmethod
    def from_parametrised_heuristic(heuristic: ParametrisedHeuristic) -> 'HeuristicCombinatorFromCallable':
        if isinstance(heuristic, ParametrisedHeuristicFromCallable):
            return HeuristicCombinatorFromCallable(
                heuristic.heuristic_callable,
                heuristic.nr_of_parameters,
                heuristic.nr_of_parameters
            )

        return HeuristicCombinatorFromCallable(
            heuristic.run,
            heuristic.nr_of_parameters,
            heuristic.nr_of_parameters
        )

    @staticmethod
    def from_pure_combinator(pure_combinator: Callable[[float], float], override_nr_of_inputs: int = -1) -> 'HeuristicCombinatorFromPureCombinator':
        return HeuristicCombinatorFromPureCombinator(
            pure_combinator, override_nr_of_inputs
        )



@dataclass
class HeuristicCombinatorFromCallable(HeuristicCombinator, ParametrisedHeuristicFromCallable):

    _nr_of_static_parameters: int

    def __init__(self, heuristic: Callable, nr_of_static_parameters: int = 0, override_nr_of_parameters: int = -1):
        super().__init__(heuristic, override_nr_of_parameters)
        assert self.nr_of_parameters >= nr_of_static_parameters, "The number of parameters can't be greater than the total number of floats"
        self._nr_of_static_parameters = nr_of_static_parameters

    @property
    def nr_of_static_parameters(self) -> int:
        return self._nr_of_static_parameters

    def run(self, state: GameState, ctx: dict, *args: float) -> float:
        return float(self.heuristic_callable(state, ctx, *args))


@dataclass
class HeuristicCombinatorFromPureCombinator(HeuristicCombinator):

    pure_combinator: Callable[[float], float]
    _nr_of_parameters: int
    _nr_of_static_parameters: int

    def __init__(self, pure_combinator: Callable[[float], float], override_nr_of_inputs: int = -1, nr_of_static_parameters: int = 0):
        self.pure_combinator = pure_combinator
        if override_nr_of_inputs == -1:
            self._nr_of_parameters = len(signature(pure_combinator).parameters)
        else:
            self._nr_of_parameters = override_nr_of_inputs
        assert self.nr_of_parameters >= nr_of_static_parameters, "The number of parameters can't be greater than the total number of floats"
        self._nr_of_static_parameters = nr_of_static_parameters

    @property
    def nr_of_parameters(self) -> int:
        return self._nr_of_parameters

    @property
    def nr_of_static_parameters(self) -> int:
        return self._nr_of_static_parameters


    def run(self, state: GameState, ctx: dict, *args: float) -> float:
        return float(self.pure_combinator(*args))



default_combinators: List[HeuristicCombinator] = [
    HeuristicCombinator.from_pure_combinator(float.__add__),
    HeuristicCombinator.from_pure_combinator(float.__mul__),
    HeuristicCombinator.from_pure_combinator(float.__sub__),
    HeuristicCombinator.from_pure_combinator(math.sin),
    HeuristicCombinator.from_pure_combinator(math.tan), # TODO@ask: should we include this despite the singularities?
    HeuristicCombinatorFromPureCombinator(lambda x: x, 1, 1), # TODO@ask: can this be here, even though, it is a leaf operation?
    HeuristicCombinator.from_pure_combinator(lambda x: max(x, 0)), # TODO@ask: I would like to include this
    HeuristicCombinator.from_pure_combinator(math.tanh), # TODO@ask: I would like to include this
]
