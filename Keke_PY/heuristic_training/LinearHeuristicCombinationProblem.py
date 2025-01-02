from typing import List, Tuple, Union, Iterable

import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import Problem
from pymoo.optimize import minimize

from Keke_PY.search_agents.AStar import AStar
from Keke_PY.heuristics.hand_crafted_heuristics import heuristics_feature_vector_length
from Keke_PY.heuristics.weighted_sum import weighted_heuristic_sum
from Keke_PY.baba import GameState, parse_map, make_level
from Keke_PY.simulation import load_level_set


class LinearHeuristicCombinationProblem(Problem):
    level_batches: List[List[str]]
    max_forward_model_calls: int


    def __init__(self, level_batches: List[List[str]], max_forward_model_calls: int = 2000):
        self.level_batches = level_batches
        self.max_forward_model_calls = max_forward_model_calls

        super().__init__(
            n_var = heuristics_feature_vector_length,
            n_obj = len(level_batches),
            n_ieq_constr = 0,
            xl = -10.0, xu = 10.0
        )

    def _evaluate(self, x, out, *args, **kwargs):

        # this output is supposed to be minimized:
        out["F"] = np.zeros((len(x), len(self.level_batches)))

        # TODO: can the following loops be parallelized?
        for batch_nr, batch in enumerate(self.level_batches):
            forward_model_calls_normalization_factor: float = 1.0 / (self.max_forward_model_calls * len(batch))
            for level_nr, level in enumerate(batch):
                start_state: GameState = make_level(parse_map(level))
                for agent_nr, agentFeatureVector in enumerate(x):
                    agent: AStar = AStar(
                        lambda game_state, ctx: weighted_heuristic_sum(
                            game_state, ctx,
                            agentFeatureVector,
                            0.5
                        )
                    )
                    solution: Tuple[Union[List[str], None], int] = agent.search(start_state, self.max_forward_model_calls, None, False)
                    forward_model_calls: int = solution[1]
                    print(agent_nr, batch_nr, level_nr, forward_model_calls)
                    penalty: float = forward_model_calls * forward_model_calls_normalization_factor
                    out["F"][agent_nr, batch_nr] += penalty

        # There are no constrains:
        out["G"] = np.zeros((len(x), 0))





# Test this class:
if __name__ == "__main__":
    test_files_as_batches: List[Tuple[str, Union[range, int, None, Iterable[int]]]] = [
        (
            "./json_levels/demo_LEVELS.json",
            [i for i in range(14) if i not in range(1, 100)]
        ), (
            "./json_levels/test_LEVELS.json",
            [i for i in range(0, 134) if i not in range(1, 1000)]
        )
    ]

    test_batches: List[List[str]] = []

    for file_name, level_nrs in test_files_as_batches:
        batch: List[str] = []
        level_set = load_level_set(file_name)
        if level_nrs is None:
            level_nrs = range(len(level_set["levels"]))
        if level_nrs.__class__ == int:
            level_nrs = range(level_nrs, level_nrs + 1)
        for index in level_nrs:
            demo_level: str = level_set["levels"][index]["ascii"]
            batch.append(demo_level)
        test_batches.append(batch)

    test_problem = LinearHeuristicCombinationProblem(test_batches, 2000)

    optimization_algorithm = NSGA2(pop_size=10)

    minimize(test_problem, optimization_algorithm)