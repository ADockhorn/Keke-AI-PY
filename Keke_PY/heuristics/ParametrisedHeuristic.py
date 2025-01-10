from abc import ABC, abstractmethod
from dataclasses import dataclass
from collections.abc import Callable
from inspect import signature

from Keke_PY.baba import GameState

class ParametrisedHeuristic(ABC):

    @property
    @abstractmethod
    def nr_of_parameters(self) -> int:
        pass

    @abstractmethod
    def run(self, state: GameState, ctx: dict, *args: float) -> float:
        pass

    @staticmethod
    def from_func(heuristic: Callable, override_nr_of_parameters: int = -1) -> 'ParametrisedHeuristicCallableWrapper':
        return ParametrisedHeuristicCallableWrapper(heuristic, override_nr_of_parameters)


@dataclass
class ParametrisedHeuristicCallableWrapper(ParametrisedHeuristic):
    heuristic_callable: Callable
    _nr_of_parameters: int

    def __init__(self, heuristic: Callable, override_nr_of_parameters: int = -1):
        self.heuristic_callable = heuristic
        if override_nr_of_parameters == -1:
            self._nr_of_parameters = len(signature(heuristic).parameters) - 2
        else:
            self._nr_of_parameters = override_nr_of_parameters

    @property
    def nr_of_parameters(self) -> int:
        return self._nr_of_parameters

    def run(self, state: GameState, ctx: dict, *args: float) -> float:
        return self.heuristic_callable(state, ctx, *args)

