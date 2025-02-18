from copy import deepcopy
from typing import List

from Keke_PY.keke_game.keke import GameState
from Keke_PY.heuristics.ParametrisedHeuristic import Heuristic
from Keke_PY.heuristics.hand_crafted_heuristics import heuristics, heuristics_feature_vector_length


class WeightedHeuristicSum(Heuristic):

    weights: List[float]
    do_nothing_threshold: float

    def __init__(self, weights: List[float], do_nothing_threshold: float = 0.01):
        assert len(weights) == heuristics_feature_vector_length
        self.weights = deepcopy(list(weights))
        self.do_nothing_threshold = do_nothing_threshold


    def run(self, state: GameState, ctx: dict, *args: float) -> float:
        feature_sum: float = 0.0
        weights_read_index: int = 0
        for heuristic in heuristics:
            weight: float = self.weights[weights_read_index]
            weights_read_index += 1
            if abs(weight) <= self.do_nothing_threshold:
                weights_read_index += heuristic.nr_of_parameters
            else:
                additional_parameters: List[float] = self.weights[
                    weights_read_index : weights_read_index + heuristic.nr_of_parameters
                ]
                weights_read_index += heuristic.nr_of_parameters
                feature_sum += weight * heuristic.run(state, ctx, *additional_parameters)
        return feature_sum

