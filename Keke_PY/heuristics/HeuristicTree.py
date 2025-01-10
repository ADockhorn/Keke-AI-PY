import random
from typing import List

from Keke_PY.baba import GameState
from Keke_PY.heuristics.HeuristicCombinator import HeuristicCombinator
from Keke_PY.heuristics.ParametrisedHeuristic import ParametrisedHeuristic


class HeuristicTreeNode(ParametrisedHeuristic):
    combinator: HeuristicCombinator
    parameters: List[float]
    children: List['HeuristicTreeNode']

    def __init__(
            self,
            combinator: HeuristicCombinator,
            children: List['HeuristicTreeNode'] = (),
            parameters: List[float] = ()
    ):
        assert len(children) == combinator.nr_of_dynamic_inputs, "The number of children of a node should be the same as inputs for the operator"
        assert len(parameters) == combinator.nr_of_static_parameters, "The number of parameters of a node should be the same as parameters for the operator"
        self.combinator = combinator
        self.children = children
        self.parameters = parameters

    @property
    def nr_of_parameters(self) -> int:
        return 0

    def run(self, state: GameState, ctx: dict, *args: float) -> float:
        return self.combinator.run(
            state, ctx,
            *self.parameters,
            *[child.run(state, ctx) for child in self.children]
        )



    @classmethod
    def with_random_params(
            cls,
            combinator: HeuristicCombinator,
            start: float, stop: float,
            children: List['HeuristicTreeNode'] = (),
    ) -> 'HeuristicTreeNode':
        return cls(combinator, children, [random.uniform(start, stop) for _ in range(combinator.nr_of_static_parameters)])
