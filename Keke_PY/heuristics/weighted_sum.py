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
        weights_read_index += 1
        if abs(weight) <= do_nothing_threshold:
            weights_read_index += heuristic.nr_of_parameters
        else:
            additional_parameters: List[float] = weights[
                weights_read_index : weights_read_index + heuristic.nr_of_parameters
            ]
            weights_read_index += heuristic.nr_of_parameters
            feature_sum += weight * heuristic.run(state, ctx, *additional_parameters)
    return feature_sum
