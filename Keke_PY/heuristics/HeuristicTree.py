import random
from copy import deepcopy
from dataclasses import dataclass
from typing import List, TypeVar, Generic, Union, Iterator, Tuple

import numpy as np
from pymoo.core.duplicate import ElementwiseDuplicateElimination

from Keke_PY.baba import GameState
from Keke_PY.heuristics.HeuristicCombinator import HeuristicCombinator, default_combinators
from Keke_PY.heuristics.ParametrisedHeuristic import ParametrisedHeuristic
from Keke_PY.heuristics.hand_crafted_heuristics import heuristics

from pymoo.core.sampling import Sampling as PymooSampling
from pymoo.core.mutation import Mutation as PymooMutation
from pymoo.core.crossover import Crossover as PymooCrossover


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
        assert \
            all([child.nr_of_parameters == 0 for child in self.children]),\
            "All child notes have to expect zero additional parameters."

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
    ):
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


    class Sampling(PymooSampling):
        def _do(self, problem, n_samples, **kwargs):
            max_depth: int = problem.max_depth
            res = np.full((n_samples, 1), None, dtype=object)
            for i in range(n_samples):
                res[i, 0] = create_random_tree(max_depth)
            return res

    class Mutation(PymooMutation):
        def __init__(self):
            super().__init__()
        def _do(self, problem, X, **kwargs):
            max_depth: int = problem.max_depth
            # for each individual
            for i in range(len(X)):
                X[i, 0] = mutation(X[i, 0], max_depth)
            return X

    class Crossover(PymooCrossover):
        def __init__(self):
            # define the crossover: number of parents and number of offsprings
            super().__init__(2, 2)
        def _do(self, problem, X, **kwargs):
            # The input of has the following shape (n_parents, n_matings, n_var)
            _, n_matings, n_var = X.shape
            max_depth: int = problem.max_depth
            # The output with the shape (n_offsprings, n_matings, n_var)
            # Because there the number of parents and offsprings are equal it keeps the shape of X
            res = np.full_like(X, None, dtype=object)
            # for each mating provided
            for k in range(n_matings):
                # get the first and the second parent
                parent1, parent2 = X[0, k, 0], X[1, k, 0]
                offspring1: HeuristicTree = crossover(parent1, parent2, max_depth)
                offspring2: HeuristicTree = crossover(parent2, parent1, max_depth)
                res[0, k, 0], res[1, k, 0] = offspring1, offspring2
            return res

    class DuplicationElimination(ElementwiseDuplicateElimination):
        def is_equal(self, a, b):
            return a.X[0] == b.X[0]



"""
The following code was originally copied from
https://github.com/AlbrErik/bachelor-thesis/blob/4680deba885c282a94643b0812f2206f0fb2dba7/KekeCompetition-main/OptimizingKekeAgents/gpmodule.py

I have changed it for compatibility with my own Code, and naming-conventions.
I have replaced the data-types, and changed the code to match.
But the functionality should have stayed broadly the same.
"""


def create_random_tree(
        depth: int,
        operations: List[DefaultOpRepr] = default_comb_operations,
        leaf_operations: List[DefaultOpRepr] = default_leaf_operations
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
    replace_subtree(first_sub[1], second_sub[1])
    res.update_depth()
    # first.update({'p1': trees[0]['id'], 'p2': trees[1]['id']}) # TODO@ask: sollen die "Stambäume" irgendwie festgehalten werden?
    return res

def mutation(
        tree: HeuristicTree,
        max_depth,
        ops: List[DefaultOpRepr] = default_comb_operations,
        heu: List[DefaultOpRepr] = default_leaf_operations
) -> HeuristicTree:
    t: HeuristicTree = deepcopy(tree)
    del_tree = random.choice(get_all_subtrees(t))
    if del_tree[0] == max_depth:
        depth = 0
    else:
        depth = random.randint(1, (max_depth - del_tree[0]))
    #Creating a new tree
    new_tree = create_random_tree(depth, ops, heu)
    replace_subtree(del_tree[1], new_tree)
    t.update_depth()
    #t.update({'p1': t['id'], 'p2': 0}) # TODO@ask: sollen die "Stambäume" irgendwie festgehalten werden?
    return t

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
