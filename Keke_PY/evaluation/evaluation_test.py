from typing import Tuple, List

from Keke_PY.evaluation.evaluation import get_performance_graph_from_timeline, get_best_instance_on_batch_timeline
from Keke_PY.experiments.KekeProblem import KekeProblem
from Keke_PY.heuristic_pymoo_representations.HeuristicTreeRepresentation import HeuristicTreeRepresentation
from Keke_PY.heuristic_pymoo_representations.TrackedRepresentation import TrackedRepresentation
from Keke_PY.heuristic_pymoo_representations.WeightedHeuristicSumRepresentation import \
    WeightedHeuristicSumRepresentation

trees, tracked, file_name = [
    (False, False, "Keke_PY/experiment_logs/all_algs_trees_and_agents/full_run_30gens/linear_sum/random/soo_short_run_all_algs_and_trees_512058_0-out.txt"),
    (False, False, "Keke_PY/experiment_logs/all_algs_trees_and_agents/full_run_30gens/linear_sum/random/soo_short_run_all_algs_and_trees_512058_8-out.txt"),
    (False, True, "Keke_PY/experiment_logs/all_algs_trees_and_agents/full_run_30gens/linear_sum/GA/soo_short_run_all_algs_and_trees_512058_1-out.txt"),
    (False, True, "Keke_PY/experiment_logs/all_algs_trees_and_agents/full_run_30gens/linear_sum/GA/soo_short_run_all_algs_and_trees_512058_9-out.txt"),
    (False, False, "Keke_PY/experiment_logs/all_algs_trees_and_agents/full_run_30gens/linear_sum/DE/soo_short_run_all_algs_and_trees_512058_2-out.txt"),
    (False, False, "Keke_PY/experiment_logs/all_algs_trees_and_agents/full_run_30gens/linear_sum/DE/soo_short_run_all_algs_and_trees_512058_10-out.txt"),
    (False, False, "Keke_PY/experiment_logs/all_algs_trees_and_agents/full_run_30gens/linear_sum/ES/soo_short_run_all_algs_and_trees_512058_3-out.txt"),
    (False, False, "Keke_PY/experiment_logs/all_algs_trees_and_agents/full_run_30gens/linear_sum/ES/soo_short_run_all_algs_and_trees_512058_11-out.txt"),
    (False, False, "Keke_PY/experiment_logs/all_algs_trees_and_agents/full_run_30gens/linear_sum/PatternSearch/soo_short_run_all_algs_and_trees_512058_4-out.txt"),
    (False, False, "Keke_PY/experiment_logs/all_algs_trees_and_agents/full_run_30gens/linear_sum/PatternSearch/soo_short_run_all_algs_and_trees_512058_12-out.txt"),
    (False, False, "Keke_PY/experiment_logs/all_algs_trees_and_agents/full_run_30gens/linear_sum/Bayesian/soo_short_run_all_algs_and_trees_512058_5-out.txt"),
    (False, False, "Keke_PY/experiment_logs/all_algs_trees_and_agents/full_run_30gens/linear_sum/Bayesian/soo_short_run_all_algs_and_trees_512058_13-out.txt"),

    (True, False, "Keke_PY/experiment_logs/all_algs_trees_and_agents/full_run_30gens/trees/random/soo_short_run_all_algs_and_trees_512058_6-out.txt"),
    (True, False, "Keke_PY/experiment_logs/all_algs_trees_and_agents/full_run_30gens/trees/random/soo_short_run_all_algs_and_trees_512058_14-out.txt"),
    (True, True, "Keke_PY/experiment_logs/all_algs_trees_and_agents/full_run_30gens/trees/GA/soo_short_run_all_algs_and_trees_512058_7-out.txt"),
    (True, True, "Keke_PY/experiment_logs/all_algs_trees_and_agents/full_run_30gens/trees/GA/soo_short_run_all_algs_and_trees_512058_15-out.txt")
][2]


file = open(file_name)


log_lines: List[str] = file.readlines()

file.close()


representation = HeuristicTreeRepresentation() if trees else WeightedHeuristicSumRepresentation()
if tracked:
    representation = TrackedRepresentation(representation)
    representation.load_from_lines(log_lines)

data: KekeProblem = KekeProblem.from_log_lines(representation, log_lines)

graph: List[Tuple[int, float]] = get_performance_graph_from_timeline(
    data,
    get_best_instance_on_batch_timeline(data, 0),
    0
)
print(graph)
graph: List[Tuple[int, float]] = get_performance_graph_from_timeline(
    data,
    get_best_instance_on_batch_timeline(data, 0),
    -1
)

print(graph)