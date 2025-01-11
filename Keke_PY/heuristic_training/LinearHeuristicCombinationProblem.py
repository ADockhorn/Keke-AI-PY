from dataclasses import dataclass
from typing import List, Tuple, Union, Iterable

import numpy as np
from pymoo.core.algorithm import Algorithm
from pymoo.core.callback import Callback
from pymoo.core.problem import Problem

from Keke_PY.search_agents.AStar import AStar
from Keke_PY.heuristics.hand_crafted_heuristics import heuristics_feature_vector_length
from Keke_PY.heuristics.weighted_sum import weighted_heuristic_sum
from Keke_PY.baba import GameState, parse_map, make_level


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


class RecordTrainingCallback(Callback):

    class IterationRecord:
        @dataclass
        class AgentRecord:
            genome: [float]
            evaluations: [float]
        def __init__(self, algorithm_state: Algorithm):
            self.agents = [
                RecordTrainingCallback.IterationRecord.AgentRecord(agent.X, agent.F)
                for agent in algorithm_state.pop
            ]

    iterations: List[IterationRecord] = []

    def notify(self, algorithm_state: Algorithm):
        iteration_record = RecordTrainingCallback.IterationRecord(algorithm_state)
        self.iterations.append(iteration_record)
