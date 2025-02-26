import multiprocessing
from typing import List, Tuple, Optional

from Keke_PY.experiments.KekeProblem import KekeProblem
from Keke_PY.heuristic_pymoo_representations.HeuristicTreeRepresentation import HeuristicTreeRepresentation
from Keke_PY.heuristic_pymoo_representations.TrackedRepresentation import TrackedRepresentation
from Keke_PY.keke_game.simulation import load_level_set

levels: List[str] = [
    *[level["ascii"] for level in
      load_level_set("./json_levels/train_LEVELS.json")["levels"]],
    *[level["ascii"] for level in
      load_level_set("./json_levels/test_LEVELS.json")["levels"]],
]

def get_level_results(level_nr: int) -> KekeProblem:
    slurm_job_id: int = 523700 if level_nr != 183 else 524904
    file_name: str = f"keke_single_level_training_{slurm_job_id}_{level_nr}-out.txt"
    with open(file_name) as file:
        lines: [str] = file.readlines()
    representation: TrackedRepresentation = TrackedRepresentation(
        HeuristicTreeRepresentation()
    )
    representation.load_from_lines(lines)
    split_index: int = lines.index("-----!!!NEW PROBLEM!!!-----\n")
    training_lines, testing_lines = lines[:split_index], lines[split_index:]
    training_data: KekeProblem = KekeProblem.from_log_lines(representation, training_lines)
    assert training_data.training_batches[0][0] == levels[level_nr]
    testing_data: KekeProblem = KekeProblem.from_log_lines(representation, testing_lines)
    print(f"reading in level {level_nr + 1} of {len(levels)} done.")
    return testing_data



if __name__ == '__main__':

    print("\n---READING IN DATA---\n")

    level_data_list: List[KekeProblem] = multiprocessing.Pool(8).map(
        get_level_results, range(len(levels))
    )

    print("\n---EVALUATION---\n")
    for result in level_data_list:
        evaluations: List[str] = []
        for lvl in levels:
            evaluation: Tuple[Optional[List[str]], int] = result.past_evaluations_by_gen_index_and_level_id[
                (0, 0, result.level_to_id_map[lvl])
            ]
            if evaluation[0] is None:
                evaluations.append("----")
            else:
                evaluations.append(str(evaluation[1]))
        print("LEVEL AGENT EVALUATION:" + '\t:'.join(evaluations))
