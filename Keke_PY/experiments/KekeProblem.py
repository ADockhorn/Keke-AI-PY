import itertools
import math
from concurrent.futures import Executor, ProcessPoolExecutor
from copy import deepcopy
from itertools import chain
from math import floor
from typing import List, Tuple, Dict, Union

import numpy as np
from pymoo.core.problem import Problem

from Keke_PY.keke_game.keke import GameState, make_level, parse_map
from Keke_PY.heuristic_pymoo_representations.HeuristicRepresentation import HeuristicRepresentation
from Keke_PY.keke_game.simulation import load_level_set
from Keke_PY.search_agents.HeuristicGuidedSearch import HeuristicGuidedSearch
from Keke_PY.search_agents.ai_interface import AgentFromPolicy, AIInterface


class KekeProblem(Problem):

    training_batches: List[List[str]]
    test_batch: List[str]
    all_levels: List[str]

    max_node_expansions: int

    executor: Executor

    representation: HeuristicRepresentation
    agent_factory: AgentFromPolicy

    generation: int = 0

    past_instances_by_gen_and_index: Dict[Tuple[int, int], np.ndarray] = {}
    past_evaluations_by_gen_index_and_level_id: Dict[Tuple[int, int, int], Tuple[Union[List[str], None], int]] = {}


    def __init__(
            self,
            training_batches: List[List[str]],
            representation: HeuristicRepresentation,
            max_node_expansions: int = 2000,
            executor: Executor = ProcessPoolExecutor(),
            test_batch: List[str] = (),
            agent_factory: AgentFromPolicy = HeuristicGuidedSearch.GuidedSearchFactory(),
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
        self.agent_factory = agent_factory

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
            limit_levels: int = None,
            agent_factory: AgentFromPolicy = HeuristicGuidedSearch.GuidedSearchFactory(),
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
            test_batch=test_levels,
            agent_factory=agent_factory
        )

    def run_as_next_generation(self, instances: [AIInterface]):
        simulation_data_list: List[Tuple[Tuple[int, AIInterface], str, int]] = list(itertools.product(
            enumerate(instances),
            self.all_levels,
            [self.max_node_expansions]
        ))
        simulation_results: Dict[Tuple[int, str], Tuple[Union[List[str], None], int]] = dict(list(self.executor.map(
            evaluate_ai_on_level, simulation_data_list
        )))
        self.past_evaluations_by_gen_index_and_level_id.update(((self.generation, key[0], self._level_to_id_map[key[1]]), result) for key, result in simulation_results.items())
        self.log_simulation_data(simulation_results)

        self.generation += 1

    def register_and_run_next_generation(self, instances: [np.ndarray]):

        self.log_generation_data(list(instances))
        self.past_instances_by_gen_and_index.update(((self.generation, index), deepcopy(instance)) for index, instance in enumerate(instances))

        self.run_as_next_generation(
            map(lambda arr: self.agent_factory.make_agent_from_policy(self.representation.into_heuristic(arr)), instances)
        )

    def _evaluate(self, x, out, *args, **kwargs):

        self.register_and_run_next_generation(x)

        performance_of_instance_on_batch: Dict[Tuple[int, int], float] = self.get_performance_of_instance_on_batch()

        # this output is supposed to be minimized:
        out["F"] = np.zeros((len(x), len(self.training_batches)))

        for batch_nr in range(len(self.training_batches)):
            for agent_nr in range(len(x)):
                out["F"][agent_nr, batch_nr] = -performance_of_instance_on_batch[(agent_nr, batch_nr)]

        # There are no constrains:
        out["G"] = np.zeros((len(x), 0))


    def get_performance_of_instance_on_batch(
            self,
            generation: int = -1
    ) -> Dict[Tuple[int, int], float]:
        if generation == -1:
            generation = self.generation - 1

        nr_of_instances: int = max(
            key[1]
            for key in self.past_evaluations_by_gen_index_and_level_id.keys()
            if key[0] == generation
        ) + 1

        performance_of_instance_on_batch: Dict[Tuple[int, int], float] = {}

        for batch_nr, batch in itertools.chain([(-1, self.test_batch)], enumerate(self.training_batches)):
            nr_of_levels: int = len(batch)
            for agent_nr in range(nr_of_instances):
                if nr_of_levels == 0:
                    performance_of_instance_on_batch[(agent_nr, batch_nr)] = math.nan
                    continue
                total_expansions: int = sum(
                    self.past_evaluations_by_gen_index_and_level_id[
                        (generation, agent_nr, self._level_to_id_map[level])
                    ][1]
                    for level in batch
                )
                average_expansions: float = total_expansions / nr_of_levels
                average_leftover_expansions: float = self.max_node_expansions - average_expansions
                nr_of_solved_levels: int = sum(
                    self.past_evaluations_by_gen_index_and_level_id[
                        (generation, agent_nr, self._level_to_id_map[level])
                    ][0] is not None
                    for level in batch
                )
                ration_of_solved_levels: float = nr_of_solved_levels / nr_of_levels
                solved_level_bonus: float = ration_of_solved_levels * self.max_node_expansions
                performance_of_instance_on_batch[(agent_nr, batch_nr)] = average_leftover_expansions + solved_level_bonus

        return performance_of_instance_on_batch

    def get_performances_of_all_generations_instances_and_batches(self) -> Dict[Tuple[int, int, int], float]:
        res: Dict[Tuple[int, int, int], float] = {}
        for generation in range(self.generation):
            res.update(
                ((generation, index, batch), performance)
                for (index, batch), performance in self.get_performance_of_instance_on_batch(generation).items()
            )
        return res

    def get_best_past_individuals(self, batch: int = 0) -> List[Tuple[int, int]]:
        performances: Dict[Tuple[int, int, int], float] = self.get_performances_of_all_generations_instances_and_batches()
        best_instances: List[Tuple[int, int]] = []
        best_performance: float = -math.inf
        for (generation, index, batch_nr), performance in performances.items():
            if batch_nr == batch:
                if performance > best_performance:
                    best_instances = [(generation, index)]
                    best_performance = performance
                elif performance == best_performance:
                    best_instances.append((generation, index))
        return best_instances


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
                all_levels[int(level_id)] = level.strip().replace('\\n', '\n')
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
        res: KekeProblem = cls(training_batches, representation, max_node_expansions, executor, test_batch)
        for line in lines:
            if line.startswith("EVAL_INSTANCE:"):
                _, generation, index, serialized_instance = line.split(':')
                cls.update = res.past_instances_by_gen_and_index.update(
                    [((int(generation), int(index)), representation.deserialize(serialized_instance))])
                res.generation = max(res.generation, int(generation) + 1)
            if line.startswith("RUN_RESULT:"):
                _, generation, index, old_level_id, *result = line.split(':')
                new_level_id: int = res._level_to_id_map[all_levels[int(old_level_id)]]
                solution: Union[List[str], None]
                node_expansions: int
                assert result is not None, f"Unexpected value in : {line}"
                if len(result) == 1:
                    # old style logging
                    result: str = result[0].strip()
                    if result == "----":
                        node_expansions = max_node_expansions
                        solution = None
                    else:
                        assert result.isdigit(), f"Unexpected value in '{result}'"
                        node_expansions = int(result)
                        solution = ["solution was not logged"]
                else:
                    # new style logging
                    assert len(result) == 2, f"Unexpected value in : {line}"
                    str_node_expansions, str_solution = result
                    str_solution = str_solution.strip()
                    assert str_node_expansions.isdigit(), f"Unexpected value in : {line}"
                    node_expansions = int(str_node_expansions)
                    if str_solution == "----":
                        solution = None
                    else:
                        solution = list(iter(str_solution))
                result: Tuple[Union[List[str], None], int] = (solution, node_expansions)
                res.past_evaluations_by_gen_index_and_level_id.update([(
                    (int(generation), int(index), new_level_id),
                    result
                )])
        return res

    def log_generation_data(self, x: list):
        for index, instance in enumerate(x):
            self.log_line(f"EVAL_INSTANCE:{self.generation}:{index}:{self.representation.serialize(instance)}")

    def log_simulation_data(self, simulation_results: Dict[Tuple[int, str], Tuple[Union[List[str], None], int]]):
        for (index, level), (solution, forward_model_calls) in simulation_results.items():
            solution_str: str = '----' if solution is None else ''.join(sol[0] for sol in solution)
            self.log_line(f"RUN_RESULT:{self.generation}:{index}:{self._level_to_id_map[level]}:{forward_model_calls}:{solution_str}")

    def log_performances(self, performance_of_instance_on_batch: Dict[Tuple[int, int], float]):
        nr_of_instances: int = max(key[0] for key in performance_of_instance_on_batch.keys()) + 1
        for batch_nr, batch in itertools.chain([(-1, self.test_batch)], enumerate(self.training_batches)):
            performances_on_batch: str = "\t|\t".join(
                str(performance_of_instance_on_batch[(instance, batch_nr)]) for instance in range(nr_of_instances)
            )
            self.log_line(f"PERFORMANCE:{self.generation}:{batch_nr}:\t{performances_on_batch}")


def evaluate_ai_on_level(
    simulation_data: Tuple[Tuple[int, AIInterface], str, int]
) -> Tuple[Tuple[int, str], Tuple[Union[List[str], None], int]]:
    ai_index: int = simulation_data[0][0]
    agent: AIInterface = simulation_data[0][1]
    level: str = simulation_data[1]
    max_forward_model_calls: int = simulation_data[2]
    start_state: GameState = make_level(parse_map(level))
    solution: Tuple[Union[List[str], None], int] = agent.search(
        start_state,
        max_forward_model_calls,
        None,
        False
    )
    #print((ai_index, level), solution[0], solution[0], solution[1])
    return (ai_index, level), solution
