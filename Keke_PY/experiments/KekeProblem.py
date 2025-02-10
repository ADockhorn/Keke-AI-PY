import itertools
from concurrent.futures import Executor, ProcessPoolExecutor
from itertools import chain
from typing import List, Tuple, Dict, Union

import numpy as np
from pymoo.core.problem import Problem

from Keke_PY.keke_game.baba import GameState, make_level, parse_map
from Keke_PY.heuristic_pymoo_representations.HeuristicRepresentation import HeuristicRepresentation
from Keke_PY.heuristics.ParametrisedHeuristic import Heuristic
from Keke_PY.search_agents.AStar import AStar


class KekeProblem(Problem):

    training_batches: List[List[str]]
    test_batch: List[str]
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
            test_batch: List[str] = ()
    ):
        assert all(len(batch) > 0 for batch in training_batches)
        self.training_batches = training_batches
        self.test_batch = test_batch
        self.max_forward_model_calls = max_forward_model_calls
        training_levels = set(chain(*training_batches))
        assert all(level not in training_levels for level in test_batch), "Training on test-levels is not allowed!"
        self.all_levels = list(training_levels) + test_batch
        self._level_to_id_map: Dict[str, int] = dict(map(lambda t: (t[1], t[0]), enumerate(self.all_levels)))
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

        self.log_level_data()

    def _evaluate(self, x, out, *args, **kwargs):

        self.log_generation_data(list(x))

        simulation_data_list: List[Tuple[Tuple[int, Heuristic], str, int]] = list(itertools.product(
            enumerate(map(lambda arr: self.representation.into_heuristic(arr), x)),
            self.all_levels,
            [self.max_forward_model_calls]
        ))

        simulation_results: Dict[Tuple[int, str], int] = dict(list(self.executor.map(
            evaluate_ai_on_level, simulation_data_list
        )))

        self.log_simulation_data(simulation_results)

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

        self.generation += 1


    def log_line(self, line: str):
        # TODO: the following line should be done by the caller
        line = line.replace('\\','\\\\').replace('\n', '\\n')
        assert len(line.split('\n')) == 1
        print(line)


    def log_level_data(self):
        for level_id, level in enumerate(self.all_levels):
            self.log_line(f"LEVEL:{level_id}:{level}")
        for batch_id, batch in chain(enumerate(self.training_batches), [(-1, self.test_batch)]):
            for index, level in enumerate(batch):
                level_id = self._level_to_id_map[level]
                assert self.all_levels[level_id] == level
                self.log_line(f"BATCH:{batch_id}:{index}:{level_id}")
    
    @classmethod
    def from_log_lines(
            cls,
            representation: HeuristicRepresentation,
            lines: List[str],
            max_forward_model_calls: int = 2000,
            executor: Executor = ProcessPoolExecutor()
    ):
        all_levels: Dict[int, str] = {}
        batches: List[Tuple[int, int, int]] = []
        for line in lines:
            if line.startswith("LEVEL:"):
                _, level_id, level = line.split(':')
                all_levels[int(level_id)] = level
            elif line.startswith("BATCH:"):
                _, batch_id, index, level_id = line.split(':')
                batches.append((int(batch_id), int(index), int(level_id)))
        training_batches: List[List[str]] = []
        test_batch: List[str] = []
        batches.sort()
        for batch_id, index, level_id in batches:
            while batch_id >= len(training_batches):
                training_batches.append([])
            batch: List[str] = test_batch if batch_id == -1 else training_batches[batch_id]
            assert index == len(batch)
            batch.append(all_levels[level_id])
        return cls(training_batches, representation, max_forward_model_calls, executor, test_batch)

    def log_generation_data(self, x: list):
        for index, instance in enumerate(x):
            self.log_line(f"EVAL_INSTANCE:{self.generation}:{index}:{self.representation.serialize(instance)}")

    def log_simulation_data(self, simulation_results: Dict[Tuple[int, str], int]):
        for (index, level), forward_model_calls in simulation_results.items():
            self.log_line(f"RUN_RESULT:{self.generation}:{index}:{self._level_to_id_map[level]}:{forward_model_calls}")


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
    #print((ai_index, level), solution[0], forward_model_calls)
    return (ai_index, level), forward_model_calls
