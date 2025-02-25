import math
from typing import Dict, List, Tuple, Optional

from Keke_PY.experiments.KekeProblem import KekeProblem


def get_best_instance_on_batch_timeline(
        data: KekeProblem,
        batch: 0
) -> List[Tuple[int, Tuple[int, int]]]:
    performances: Dict[Tuple[int, int, int], float] = data.get_performances_of_all_generations_instances_and_batches()
    current_individual: Optional[Tuple[int, int]] = None
    current_performance: float = -math.inf
    cumulative_evaluations: int = 0
    res: List[Tuple[int, Tuple[int, int]]] = []
    for generation in range(data.generation):
        generation_size: int = max(
            individual
            for gen, individual, _ in performances.keys()
            if gen == generation
        ) + 1
        cumulative_evaluations += generation_size
        best_individual_changed: bool = False
        for individual in range(generation_size):
            if performances[(generation, individual, batch)] > current_performance:
                current_individual = (generation, individual)
                current_performance = performances[(generation, individual, batch)]
                best_individual_changed = True
        if best_individual_changed:
            res.append((cumulative_evaluations, current_individual))
    return res

def get_performance_graph_from_timeline(
        data: KekeProblem,
        timeline: List[Tuple[int, Tuple[int, int]]],
        batch: int = -1
) -> List[Tuple[int, float]]:
    performances: Dict[Tuple[int, int, int], float] = data.get_performances_of_all_generations_instances_and_batches()
    return [
        (past_evaluations, performances[(gen, i, batch)])
        for past_evaluations, (gen, i) in timeline
    ]