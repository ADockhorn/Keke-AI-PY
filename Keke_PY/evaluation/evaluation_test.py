from typing import Tuple, List

from matplotlib import pyplot as plt

from Keke_PY.evaluation.evaluation import get_performance_graph_from_timeline, get_best_instance_on_batch_timeline
from Keke_PY.experiments.KekeProblem import KekeProblem
from Keke_PY.heuristic_pymoo_representations.HeuristicTreeRepresentation import HeuristicTreeRepresentation
from Keke_PY.heuristic_pymoo_representations.TrackedRepresentation import TrackedRepresentation
from Keke_PY.heuristic_pymoo_representations.WeightedHeuristicSumRepresentation import \
    WeightedHeuristicSumRepresentation


setups: List[Tuple[bool, bool, str]] = [
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
]

def show_training_graph(
        trees: bool, tracked: bool, file_name: str,
        select_best_by_batch: int = 0, show_performance_on_batch: int = -1,
):
    print(f"generating graph for '{file_name}'")
    with open(file_name) as file:
        log_lines: List[str] = file.readlines()
    representation = HeuristicTreeRepresentation() if trees else WeightedHeuristicSumRepresentation()
    if tracked:
        representation = TrackedRepresentation(representation)
        representation.load_from_lines(log_lines)
    problem_data: KekeProblem = KekeProblem.from_log_lines(representation, log_lines)
    plot_data: List[Tuple[int, float]] = get_performance_graph_from_timeline(
        problem_data,
        get_best_instance_on_batch_timeline(problem_data, select_best_by_batch),
        show_performance_on_batch
    )

    plot_points: List[Tuple[int, float]] = [(0, 0.0)]
    for i, (iterations, performance) in enumerate(plot_data):
        plot_points.append((iterations, plot_points[-1][1]))
        plot_points.append((iterations, performance))
    plot_points.append((300, plot_points[-1][1]))


    plt.style.use('_mpl-gallery')
    fig, ax = plt.subplots()
    ax.plot(*zip(*plot_points), linewidth=2.0)
    ax.set(
        xlim=(0, 300),
        ylim=(0, 4000),
    )
    plt.show()







for setup in setups:
    show_training_graph(*setup)