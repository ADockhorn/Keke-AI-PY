import itertools
from concurrent.futures import Executor, ProcessPoolExecutor
from itertools import chain
from typing import List, Tuple, Union, Dict

import numpy as np
from pymoo.core.problem import Problem

from Keke_PY.heuristics.HeuristicRepresentation import HeuristicRepresentation
from Keke_PY.heuristics.ParametrisedHeuristic import Heuristic
from Keke_PY.search_agents.AStar import AStar
from Keke_PY.baba import GameState, parse_map, make_level


class KekeProblem(Problem):

    training_batches: List[List[str]]
    test_batch: [str]
    all_levels: List[str]

    max_forward_model_calls: int

    executor: Executor

    representation: HeuristicRepresentation

    generation: int = 0


    def __init__(
            self,
            training_batches: List[List[str]],
            representation: HeuristicRepresentation,
            max_forward_model_calls: int = 2000,
            executor: Executor = ProcessPoolExecutor(),
            test_batch: [str] = ()
    ):
        self.training_batches = training_batches
        self.test_batch = test_batch
        self.max_forward_model_calls = max_forward_model_calls
        self.all_levels = list(set(chain(test_batch, *training_batches)))
        self.representation = representation
        self.executor = executor

        problem_data: Problem = representation.get_problem_data()
        super().__init__(
            n_var = problem_data.n_var,
            n_obj = len(training_batches),
            n_ieq_constr = 0,
            xl=problem_data.xl,
            xu=problem_data.xu,
            vtype=problem_data.vtype,
        )

    def _evaluate(self, x, out, *args, **kwargs):
        self.generation += 1

        self.log_generation_data(list(x))

        simulation_data_list: List[Tuple[Tuple[int, Heuristic], str, int]] = list(itertools.product(
            enumerate(map(lambda arr: self.representation.into_heuristic(arr), x)),
            self.all_levels,
            [self.max_forward_model_calls]
        ))

        simulation_results: Dict[Tuple[int, str], int] = dict(list(self.executor.map(
            evaluate_ai_on_level, simulation_data_list
        )))

        self.log_simulation_info(simulation_results)

        # this output is supposed to be minimized:
        out["F"] = np.zeros((len(x), len(self.training_batches)))

        for batch_nr, batch in enumerate(self.training_batches):
            forward_model_calls_normalization_factor: float = 1.0 / (self.max_forward_model_calls * len(batch))
            for level_nr, level in enumerate(batch):
                for agent_nr, _agentFeatureVector in enumerate(x):
                    penalty: float = simulation_results[(agent_nr, level)] * forward_model_calls_normalization_factor
                    out["F"][agent_nr, batch_nr] += penalty

        # There are no constrains:
        out["G"] = np.zeros((len(x), 0))


    def log_generation_data(self, x: list):
        for index, instance in enumerate(x):
            print("EVALUATE INSTANCE: ", {
                "gen": self.generation,
                "index": index,
                "heuristic": self.representation.serialize(instance)
            })

    def log_simulation_info(self, simulation_results: Dict[Tuple[int, str], int]):
        for (ai_id, level), forward_model_calls in simulation_results.items():
            print("EVALUATION: ", {
                "gen": self.generation,
                "index": ai_id,
                "level": level,
                "forward_model_calls": forward_model_calls
            })





def evaluate_ai_on_level(
    simulation_data: Tuple[Tuple[int, Heuristic], str, int]
) -> Tuple[Tuple[int, str], int]:
    ai_index: int = simulation_data[0][0]
    heuristic: Heuristic = simulation_data[0][1]
    level: str = simulation_data[1]
    max_forward_model_calls: int = simulation_data[2]
    start_state: GameState = make_level(parse_map(level))
    agent: AStar = AStar(heuristic)
    solution: Tuple[Union[List[str], None], int] = agent.search(
        start_state,
        max_forward_model_calls,
        None,
        False
    )
    forward_model_calls: int = solution[1]
    return (ai_index, level), forward_model_calls
