import itertools
from concurrent.futures import Executor, ProcessPoolExecutor
from dataclasses import dataclass
from itertools import chain
from typing import Tuple, List, Union, Dict

import numpy as np
from pymoo.core.algorithm import Algorithm
from pymoo.core.callback import Callback
from pymoo.core.problem import Problem

from Keke_PY.baba import GameState, make_level, parse_map
from Keke_PY.heuristics.HeuristicTree import HeuristicTree
from Keke_PY.search_agents.AStar import AStar


class HeuristicTreeProblem(Problem):

    level_batches: List[List[str]]
    all_levels: List[str]

    max_forward_model_calls: int

    executor: Executor

    max_depth: int


    def __init__(
            self,
            max_depth: int,
            level_batches: List[List[str]],
            max_forward_model_calls: int = 2000,
            executor: Executor = ProcessPoolExecutor()
    ):
        self.max_depth = max_depth
        self.level_batches = level_batches
        self.max_forward_model_calls = max_forward_model_calls
        self.all_levels = list(set(chain(*level_batches)))
        self.executor = executor

        super().__init__(
            n_var = 1,
            n_obj = len(level_batches),
            n_ieq_constr = 0
        )

    def _evaluate(self, x, out, *args, **kwargs):

        simulation_data_list: List[Tuple[Tuple[int, HeuristicTree], str, int]] = list(itertools.product(
            list(map(lambda tup: (tup[0], tup[1][0]), enumerate(x))),
            self.all_levels,
            [self.max_forward_model_calls]
        ))

        simulation_results: Dict[Tuple[int, str], int] = dict(list(self.executor.map(
            evaluate_ai_on_level, simulation_data_list
        )))

        # this output is supposed to be minimized:
        out["F"] = np.zeros((len(x), len(self.level_batches)))

        for batch_nr, batch in enumerate(self.level_batches):
            forward_model_calls_normalization_factor: float = 1.0 / (self.max_forward_model_calls * len(batch))
            for level_nr, level in enumerate(batch):
                for agent_nr, _agentHeuristicTree in enumerate(x):
                    penalty: float = simulation_results[(agent_nr, level)] * forward_model_calls_normalization_factor
                    out["F"][agent_nr, batch_nr] += penalty

        # There are no constrains:
        out["G"] = np.zeros((len(x), 0))



def evaluate_ai_on_level(
    simulation_data: Tuple[Tuple[int, HeuristicTree], str, int]
) -> Tuple[Tuple[int, str], int]:
    ai_index: int = simulation_data[0][0]
    ai: HeuristicTree = simulation_data[0][1]
    level: str = simulation_data[1]
    max_forward_model_calls: int = simulation_data[2]
    start_state: GameState = make_level(parse_map(level))
    agent: AStar = AStar(ai)
    solution: Tuple[Union[List[str], None], int] = agent.search(
        start_state,
        max_forward_model_calls,
        None,
        False
    )
    forward_model_calls: int = solution[1]
    print((ai_index, level), forward_model_calls)
    return (ai_index, level), forward_model_calls



class TrainingRecord(Callback):

    class IterationRecord:
        @dataclass
        class AgentRecord:
            tree: HeuristicTree
            evaluations: [float]
        def __init__(self, algorithm_state: Algorithm):
            self.agents = [
                TrainingRecord.IterationRecord.AgentRecord(agent.X, agent.F[0])
                for agent in algorithm_state.pop
            ]

    iterations: List[IterationRecord] = []

    def notify(self, algorithm_state: Algorithm):
        iteration_record = TrainingRecord.IterationRecord(algorithm_state)
        self.iterations.append(iteration_record)
