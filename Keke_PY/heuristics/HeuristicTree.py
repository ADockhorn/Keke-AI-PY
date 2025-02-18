import random
from copy import deepcopy
from dataclasses import dataclass
from typing import List, TypeVar, Generic, Union, Iterator, Tuple

from numpy.random import randn
from pygame.math import clamp

from Keke_PY.keke_game.keke import GameState
from Keke_PY.heuristics.HeuristicCombinator import HeuristicCombinator, default_combinators, \
    HeuristicCombinatorFromPureCombinator
from Keke_PY.heuristics.ParametrisedHeuristic import Heuristic
from Keke_PY.heuristics.hand_crafted_heuristics import heuristics



OpRepr = TypeVar('OpRepr', bound=HeuristicCombinator)
Child = TypeVar('Child', bound=Heuristic)

@dataclass
class GenericHeuristicTreeNode(Heuristic, Generic[OpRepr, Child]):
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
        assert \
            all([child.nr_of_parameters == 0 for child in self.children]),\
            "All child notes have to expect zero additional parameters."

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
    ):
        return cls(combinator, children or [], [
            random.uniform(start, stop)
            for _ in range(combinator.nr_of_static_parameters)
        ])




_raw_default_comb_ops: [HeuristicCombinator] = default_combinators
_raw_default_leaf_ops: [HeuristicCombinator] = (
    HeuristicCombinatorFromPureCombinator(lambda x: x, 1, 1), # constant
    *map(HeuristicCombinator.from_parametrised_heuristic, heuristics), # handcrafted heuristics
)

_raw_default_operations: [HeuristicCombinator] = (
    *_raw_default_comb_ops,
    *_raw_default_leaf_ops
)

@dataclass
class DefaultOpRepr(HeuristicCombinator):

    op_index: int

    @property
    def op(self) -> HeuristicCombinator:
        return _raw_default_operations[self.op_index]

    @property
    def nr_of_parameters(self) -> int:
        return self.op.nr_of_parameters

    @property
    def nr_of_static_parameters(self) -> int:
        return self.op.nr_of_static_parameters

    def run(self, state: GameState, ctx: dict, *args: float) -> float:
        return self.op.run(state, ctx, *args)


default_comb_operations: [DefaultOpRepr] = tuple(DefaultOpRepr(i) for i, op in enumerate(_raw_default_operations) if op in _raw_default_comb_ops)
default_leaf_operations: [DefaultOpRepr] = tuple(DefaultOpRepr(i) for i, op in enumerate(_raw_default_operations) if op in _raw_default_leaf_ops)



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
    def from_data(cls, data: Iterator[Union[int, float, str]]) -> 'HeuristicTree':
        operator: DefaultOpRepr = DefaultOpRepr(int(next(data)))
        parameters: List[float] = [
            float(next(data))
            for _ in range(operator.nr_of_static_parameters)
        ]
        children: List[HeuristicTree] = [
            HeuristicTree.from_data(data)
            for _ in range(operator.nr_of_dynamic_inputs)
        ]
        return cls(operator, children, parameters)



"""
The following code was originally copied from
https://github.com/AlbrErik/bachelor-thesis/blob/4680deba885c282a94643b0812f2206f0fb2dba7/KekeCompetition-main/OptimizingKekeAgents/gpmodule.py

I have changed it for compatibility with my own Code, and naming-conventions.
I have replaced the data-types, and changed the code to match.
But the functionality should have stayed broadly the same.
FUNCTIONAL CHANGE: tree nodes can have additional float properties between -10 and 10
FUNCTIONAL CHANGE: mutation adds noise on the additional float properties
"""


def create_random_tree(
        depth: int,
        operations: [DefaultOpRepr] = default_comb_operations,
        leaf_operations: [DefaultOpRepr] = default_leaf_operations
) -> HeuristicTree:
    if depth == 0:
         return HeuristicTree.with_random_params(
             random.choice(leaf_operations),
             -10.0, 10.0
         )
    #choose new root node
    operator: DefaultOpRepr = random.choice(operations)
    #add children to root node
    children = []
    for i in range(0, operator.nr_of_dynamic_inputs):
        children.append(create_random_tree(depth - 1, operations, leaf_operations))
    #return (sub)tree
    return HeuristicTree.with_random_params(operator, -10.0, 10.0, children)



def crossover(tree1: HeuristicTree, tree2: HeuristicTree, max_depth: int) -> HeuristicTree:
    if tree1.depth == 0 or tree2.depth == 0:
        # abort crossover, if any parent is too small:
        return tree1
    res: HeuristicTree = deepcopy(tree1)
    # search random subtree for removal (parent 1)
    first_sub: Tuple[int, HeuristicTree] = random.choice(get_all_subtrees(res)[1:])
    #calc max_depth for subtree in "parent 2" and choose subtree
    max_d: int = max_depth - first_sub[0]
    second_subs: List[Tuple[int, HeuristicTree]] = get_all_subtrees(tree2)
    second_subs = list(filter(lambda tup: tup[1].depth <= max_d, second_subs))
    second_sub = random.choice(second_subs)
    #replace subtree in parent 1 with subtree in parent 2
    replace_subtree(first_sub[1], deepcopy(second_sub[1]))
    res.update_depth()
    return res

def mutation(
        tree: HeuristicTree,
        max_depth,
        float_noise_factor: float,
        ops: [DefaultOpRepr] = default_comb_operations,
        heu: [DefaultOpRepr] = default_leaf_operations
) -> HeuristicTree:
    t: HeuristicTree = deepcopy(tree)
    if float_noise_factor > 0.0:
        add_noise(t, float_noise_factor)
    del_tree = random.choice(get_all_subtrees(t))
    if del_tree[0] == max_depth:
        depth = 0
    else:
        depth = random.randint(1, (max_depth - del_tree[0]))
    #Creating a new tree
    new_tree = create_random_tree(depth, ops, heu)
    replace_subtree(del_tree[1], new_tree)
    t.update_depth()
    return t

def add_noise(
        tree: HeuristicTree,
        float_noise_factor: float
):
    for i, f_value in enumerate(tree.parameters):
        tree.parameters[i] = clamp(f_value + randn() * float_noise_factor, -10.0, 10.0)
    for child in tree.children:
        add_noise(child, float_noise_factor)

def replace_subtree(tree: HeuristicTree, subtree: HeuristicTree):
    tree.combinator = subtree.combinator
    tree.parameters = subtree.parameters
    tree.children = subtree.children

def get_all_subtrees(tree: HeuristicTree, depth = 0, subtrees = None) -> List[Tuple[int, HeuristicTree]]:
    if subtrees is None:
        subtrees = []
    subtrees.append((depth, tree))
    new_depth = depth + 1
    for child in tree.children:
        get_all_subtrees(child, new_depth, subtrees)
    return subtrees
