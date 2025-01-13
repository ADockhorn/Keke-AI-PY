import random
from dataclasses import dataclass
from typing import List, TypeVar, Generic, Dict, Union, Callable, Optional, Iterator

from Keke_PY.baba import GameState
from Keke_PY.heuristics.HeuristicCombinator import HeuristicCombinator, default_combinators
from Keke_PY.heuristics.ParametrisedHeuristic import ParametrisedHeuristic
from Keke_PY.heuristics.hand_crafted_heuristics import heuristics

OpRepr = TypeVar('OpRepr', bound=HeuristicCombinator)
Child = TypeVar('Child', bound=ParametrisedHeuristic)

@dataclass
class GenericHeuristicTreeNode(ParametrisedHeuristic, Generic[OpRepr, Child]):
    combinator: OpRepr
    children: List[Child]
    parameters: List[float]

    def __post_init__(self):
        assert \
            len(self.children) == self.combinator.nr_of_dynamic_inputs,\
            "The number of children of a node should be the same as inputs for the operator"
        assert \
            len(self.parameters) == self.combinator.nr_of_static_parameters,\
            "The number of parameters of a node should be the same as parameters for the operator"

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
            combinator: OpRepr,
            start: float, stop: float,
            children: List[Child] = None,
    ) -> 'GenericHeuristicTreeNode':
        return cls(combinator, children or [], [
            random.uniform(start, stop)
            for _ in range(combinator.nr_of_static_parameters)
        ])




raw_default_operations: List[HeuristicCombinator] = [
    *default_combinators,
    *map(HeuristicCombinator.from_parametrised_heuristic, heuristics)
]

@dataclass
class DefaultOpRepr(HeuristicCombinator):

    op_index: int

    @property
    def op(self) -> HeuristicCombinator:
        return raw_default_operations[self.op_index]

    @property
    def nr_of_parameters(self) -> int:
        return self.op.nr_of_parameters

    @property
    def nr_of_static_parameters(self) -> int:
        return self.op.nr_of_static_parameters

    def run(self, state: GameState, ctx: dict, *args: float) -> float:
        return self.op.run(state, ctx, *args)


default_operations = [DefaultOpRepr(i) for i, _ in enumerate(raw_default_operations)]
default_comb_operations = [DefaultOpRepr(i) for i, _ in enumerate(default_combinators)]
default_leaf_operations = [DefaultOpRepr(len(default_combinators) + i) for i, _ in enumerate(heuristics)]



@dataclass
class HeuristicTree(GenericHeuristicTreeNode[DefaultOpRepr, 'HeuristicTree']):

    depth: int = 0

    def __post_init__(self):
        if len(self.children) > 0:
            self.depth = 1 + max(map(lambda c: c.depth, self.children))

    def update_depth(self):
        for child in self.children:
            child.update_depth()
        if len(self.children) > 0:
            self.depth = 1 + max(map(lambda c: c.depth, self.children))
        else:
            self.depth = 0

    def to_data(self) -> Iterator[Union[int, float]]:
        yield self.combinator.op_index
        for param in self.parameters:
            yield param
        for child in self.children:
            for data in child.to_data():
                yield data


    @classmethod
    def from_data(cls, data: Iterator[Union[int, float]]) -> 'HeuristicTree':
        operator: DefaultOpRepr = DefaultOpRepr(next(data))
        parameters: List[float] = [
            next(data)
            for _ in range(operator.nr_of_static_parameters)
        ]
        children: List[HeuristicTree] = [
            HeuristicTree.from_data(data)
            for _ in range(operator.nr_of_dynamic_inputs)
        ]
        return cls(operator, children, parameters)
