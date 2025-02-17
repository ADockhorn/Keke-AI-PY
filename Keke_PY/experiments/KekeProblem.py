import itertools
from concurrent.futures import Executor, ProcessPoolExecutor
from itertools import chain
from math import floor
from typing import List, Tuple, Dict, Union

import numpy as np
from pymoo.core.problem import Problem

from Keke_PY.keke_game.baba import GameState, make_level, parse_map
from Keke_PY.heuristic_pymoo_representations.HeuristicRepresentation import HeuristicRepresentation
from Keke_PY.heuristics.ParametrisedHeuristic import Heuristic
from Keke_PY.keke_game.simulation import load_level_set
from Keke_PY.search_agents.HeuristicGuidedSearch import HeuristicGuidedSearch


class KekeProblem(Problem):

    training_batches: List[List[str]]
    test_batch: List[str]
    all_levels: List[str]

    max_node_expansions: int

    executor: Executor

    representation: HeuristicRepresentation

    generation: int = 0


    def __init__(
            self,
            training_batches: List[List[str]],
            representation: HeuristicRepresentation,
            max_node_expansions: int = 2000,
            executor: Executor = ProcessPoolExecutor(),
            test_batch: List[str] = ()
    ):
        assert all(len(batch) > 0 for batch in training_batches)
        self.training_batches = training_batches
        self.test_batch = test_batch
        self.max_node_expansions = max_node_expansions
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

    @classmethod
    def default_problem(
            cls,
            representation: HeuristicRepresentation,
            executor: Executor = ProcessPoolExecutor(),
            limit_levels: int = None
    ):
        levels: List[str] = [
            *[level["ascii"] for level in
              load_level_set("./json_levels/train_LEVELS.json")["levels"]],
            *[level["ascii"] for level in
              load_level_set("./json_levels/test_LEVELS.json")["levels"]],
        ]
        if limit_levels is not None:
            levels = levels[:limit_levels]
        training_ratio: float = 0.6
        training_levels: List[str] = levels[:floor(training_ratio * len(levels))]
        test_levels: List[str] = levels[floor(training_ratio * len(levels)):]
        return cls(
            training_batches=[training_levels],
            representation=representation,
            max_node_expansions=2000,
            executor=executor,
            test_batch=test_levels
        )

    def evaluate_performance_of_instance_on_batch(self, instances: [Heuristic]) -> Dict[Tuple[int, int], float]:
        simulation_data_list: List[Tuple[Tuple[int, Heuristic], str, int]] = list(itertools.product(
            enumerate(instances),
            self.all_levels,
            [self.max_node_expansions]
        ))
        simulation_results: Dict[Tuple[int, str], Tuple[Union[List[str], None], int]] = dict(list(self.executor.map(
            evaluate_ai_on_level, simulation_data_list
        )))
        self.log_simulation_data(simulation_results)

        performance_of_instance_on_batch: Dict[Tuple[int, int], float] = self.calc_performance_of_instance_on_batch(simulation_results)

        self.log_performances(performance_of_instance_on_batch)

        return performance_of_instance_on_batch

    def _evaluate(self, x, out, *args, **kwargs):

        self.log_generation_data(list(x))

        performance_of_instance_on_batch: Dict[Tuple[int, int], float] = self.evaluate_performance_of_instance_on_batch(
            map(lambda arr: self.representation.into_heuristic(arr), x)
        )

        # this output is supposed to be minimized:
        out["F"] = np.zeros((len(x), len(self.training_batches)))

        for batch_nr in range(len(self.training_batches)):
            for agent_nr in range(len(x)):
                out["F"][agent_nr, batch_nr] = -performance_of_instance_on_batch[(agent_nr, batch_nr)]

        # There are no constrains:
        out["G"] = np.zeros((len(x), 0))

        self.generation += 1

    def calc_performance_of_instance_on_batch(
            self,
            simulation_results: Dict[Tuple[int, str], Tuple[Union[List[str], None], int]],
            nr_of_instances: int = -1
    ) -> Dict[Tuple[int, int], float]:
        if nr_of_instances == -1:
            nr_of_instances = max(key[0] for key in simulation_results.keys()) + 1

        performance_of_instance_on_batch: Dict[Tuple[int, int], float] = {}

        for batch_nr, batch in itertools.chain([(-1, self.test_batch)], enumerate(self.training_batches)):
            nr_of_levels: int = len(batch)
            for agent_nr in range(nr_of_instances):
                total_expansions: int = sum(simulation_results[(agent_nr, level)][1] for level in batch)
                average_expansions: float = total_expansions / nr_of_levels
                average_leftover_expansions: float = self.max_node_expansions - average_expansions
                nr_of_solved_levels: int = sum(simulation_results[(agent_nr, level)][0] is not None for level in batch)
                ration_of_solved_levels: float = nr_of_solved_levels / nr_of_levels
                solved_level_bonus: float = ration_of_solved_levels * self.max_node_expansions
                performance_of_instance_on_batch[(agent_nr, batch_nr)] = average_leftover_expansions + solved_level_bonus

        return performance_of_instance_on_batch



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
            max_node_expansions: int = 2000,
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
        return cls(training_batches, representation, max_node_expansions, executor, test_batch)

    def log_generation_data(self, x: list):
        for index, instance in enumerate(x):
            self.log_line(f"EVAL_INSTANCE:{self.generation}:{index}:{self.representation.serialize(instance)}")

    def log_simulation_data(self, simulation_results: Dict[Tuple[int, str], Tuple[Union[List[str], None], int]]):
        for (index, level), (solution, forward_model_calls) in simulation_results.items():
            res = '----'
            if solution is not None:
                res = forward_model_calls
            self.log_line(f"RUN_RESULT:{self.generation}:{index}:{self._level_to_id_map[level]}:{res}")

    def log_performances(self, performance_of_instance_on_batch: Dict[Tuple[int, int], float]):
        nr_of_instances: int = max(key[0] for key in performance_of_instance_on_batch.keys()) + 1
        for batch_nr, batch in itertools.chain([(-1, self.test_batch)], enumerate(self.training_batches)):
            performances_on_batch: str = "\t|\t".join(
                str(performance_of_instance_on_batch[(instance, batch_nr)]) for instance in range(nr_of_instances)
            )
            self.log_line(f"PERFORMANCE:{self.generation}:{batch_nr}:\t{performances_on_batch}")


def evaluate_ai_on_level(
    simulation_data: Tuple[Tuple[int, Heuristic], str, int]
) -> Tuple[Tuple[int, str], Tuple[Union[List[str], None], int]]:
    ai_index: int = simulation_data[0][0]
    heuristic: Heuristic = simulation_data[0][1]
    level: str = simulation_data[1]
    max_forward_model_calls: int = simulation_data[2]
    start_state: GameState = make_level(parse_map(level))
    agent: HeuristicGuidedSearch = HeuristicGuidedSearch(heuristic)
    solution: Tuple[Union[List[str], None], int] = agent.search(
        start_state,
        max_forward_model_calls,
        None,
        False
    )
    #print((ai_index, level), solution[0], solution[0], solution[1])
    return (ai_index, level), solution
