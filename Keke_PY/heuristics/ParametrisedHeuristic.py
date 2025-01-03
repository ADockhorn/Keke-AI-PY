from dataclasses import dataclass
from collections.abc import Callable
from inspect import signature

from Keke_PY.baba import GameState

@dataclass
class ParametrisedHeuristic:
    heuristic_callable: Callable
    additional_parameters: int

    def __init__(self, heuristic: Callable):
        self.heuristic_callable = heuristic
        self.additional_parameters = len(signature(heuristic).parameters) - 2

    def run(self, state: GameState, ctx: dict, *args: float) -> float:
        return self.heuristic_callable(state, ctx, *args)

