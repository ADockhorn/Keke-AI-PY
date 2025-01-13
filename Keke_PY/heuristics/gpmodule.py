"""
This code was originally copied from
https://github.com/AlbrErik/bachelor-thesis/blob/4680deba885c282a94643b0812f2206f0fb2dba7/KekeCompetition-main/OptimizingKekeAgents/gpmodule.py

I have changed it for compatibility with my own Code, and naming-conventions.
I have replaced the data-types, and changed the code to match.
But the functionality should have stayed broadly the same.
"""

import random
from copy import deepcopy

from typing import List, Tuple

from Keke_PY.heuristics.HeuristicTree import DefaultOpRepr, HeuristicTreeNode, \
    default_comb_operations, default_leaf_operations


def create_random_tree(
        depth: int,
        operations: List[DefaultOpRepr] = default_comb_operations,
        leaf_operations: List[DefaultOpRepr] = default_leaf_operations
) -> HeuristicTreeNode:
    if depth == 0:
         return HeuristicTreeNode.with_random_params(
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
    return HeuristicTreeNode.with_random_params(operator, -10.0, 10.0, children)



def crossover(tree1: HeuristicTreeNode, tree2: HeuristicTreeNode, max_depth: int) -> HeuristicTreeNode:
    res: HeuristicTreeNode = deepcopy(tree1)
    # search random subtree for removal (parent 1)
    first_sub: Tuple[int, HeuristicTreeNode] = random.choice(get_all_subtrees(res)[1:])
    #calc max_depth for subtree in "parent 2" and choose subtree
    max_d: int = max_depth - first_sub[0]
    second_subs: List[Tuple[int, HeuristicTreeNode]] = get_all_subtrees(tree2)
    second_subs = list(filter(lambda tup: tup[1].depth <= max_d, second_subs))
    second_sub = random.choice(second_subs)
    #replace subtree in parent 1 with subtree in parent 2
    replace_subtree(first_sub[1], second_sub[1])
    res.update_depth()
    # first.update({'p1': trees[0]['id'], 'p2': trees[1]['id']}) # TODO@ask: sollen die "Stambäume" irgendwie festgehalten werden?
    return res

def mutation(
        tree: HeuristicTreeNode,
        max_depth,
        ops: List[DefaultOpRepr] = default_comb_operations,
        heu: List[DefaultOpRepr] = default_leaf_operations
) -> HeuristicTreeNode:
    t: HeuristicTreeNode = deepcopy(tree)
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

def replace_subtree(tree: HeuristicTreeNode, subtree: HeuristicTreeNode):
    tree.combinator = subtree.combinator
    tree.parameters = subtree.parameters
    tree.children = subtree.children

def get_all_subtrees(tree: HeuristicTreeNode, depth = 0, subtrees = None) -> List[Tuple[int, HeuristicTreeNode]]:
    if subtrees is None:
        subtrees = []
    subtrees.append((depth, tree))
    new_depth = depth + 1
    for child in tree.children:
        get_all_subtrees(child, new_depth, subtrees)
    return subtrees
