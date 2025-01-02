from inspect import signature
from typing import List

from Keke_PY.baba import GameState
from Keke_PY.heuristics.hand_crafted_heuristics import heuristics


def weighted_heuristic_sum(
    state: GameState, ctx: dict,
    weights: List[float],
    do_nothing_threshold: float = 0.01
) -> float:
    feature_sum: float = 0.0
    weights_read_index: int = 0
    for heuristic in heuristics:
        weight: float = weights[weights_read_index]
        if abs(weight) <= do_nothing_threshold:
            weights_read_index += len(signature(heuristic).parameters) - 1
        else:
            weights_read_index += 1
            parameters: List = [state, ctx]
            for _ in range(len(signature(heuristic).parameters) - 2):
                parameters.append(weights[weights_read_index])
                weights_read_index += 1
            feature_sum += weight * heuristic(*parameters)
    return feature_sum
