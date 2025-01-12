"""
This file is copied from
https://github.com/AlbrErik/bachelor-thesis/blob/4680deba885c282a94643b0812f2206f0fb2dba7/KekeCompetition-main/OptimizingKekeAgents/gpmodule.py

I have changed it for compatibility with my own Code, and naming-conventions.
Dicts will be replaced by custom types.
But the functionality should stay broadly the same.
"""

import random
from copy import deepcopy

from typing import List

from pymoo.core.sampling import Sampling

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



def crossover(trees: list, max_depth):
    first = deepcopy(trees[0])
    second = deepcopy(trees[1])
    # search random subtree for removal (parent 1)
    first_subs = get_all_subtrees(first)
    first_subs.pop(0)
    first_sub = random.choice(first_subs)
    #calc max_depth for subtree in "parent 2" and choose subtree
    max_d = max_depth - first_sub[0]
    second_subs = get_all_subtrees(second)
    iter_subs = deepcopy(second_subs)
    for sub in iter_subs:
        if(get_depth(sub[1]) > max_d):
            second_subs.remove(sub)
    second_sub = random.choice(second_subs)
    #replace subtree in parent 1 with subtree in parent 2
    replace_subtree(first_sub[1], second_sub[1])
    first.update({'p1': trees[0]['id'], 'p2': trees[1]['id']})
    return first

def mutation(tree: dict, ops: List[tuple], heu: List[int], max_depth):
    t = deepcopy(tree)
    del_tree = random.choice(get_all_subtrees(t))
    #Edge-Case: The whole tree is going to be deleted
    if(del_tree[0] == 0):
        depth = random.randint(1, max_depth)
    if(del_tree[0] == max_depth):
        depth = 0
    else:
        depth = random.randint(1, (max_depth - del_tree[0]))
    #Creating a new tree
    new_tree = create_random_tree(depth, ops, heu)
    replace_subtree(del_tree[1], new_tree)
    t.update({'p1': t['id'], 'p2': 0})
    return t

def get_depth(tree: dict):
    depth = 0
    if(len(tree['children']) == 0):
        return 0
    if(len(tree['children']) == 1):
        depth = 1 + get_depth(tree['children'][0])
    else:
        depth = max((1 + get_depth(tree['children'][0])), (1 + get_depth(tree['children'][1])))
    return depth

def replace_subtree(tree: dict, subtree: dict):
    tree['operation'] = subtree['operation']
    tree['children'] = subtree['children']

def get_all_subtrees(tree: dict, depth = 0, subtrees = None):
    if subtrees is None:
        subtrees = []
    subtrees.append((depth, tree))
    new_depth = depth + 1
    if(len(tree['children']) > 0):
        for child in tree['children']:
            get_all_subtrees(child, new_depth, subtrees)
    return subtrees
