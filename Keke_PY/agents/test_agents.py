from typing import Tuple, Union

from Keke_PY.agents.AStar import AStar, simple_heuristic, test_heuristics
from Keke_PY.simulation import load_level_set, parse_map, make_level
from BFS import BFS
from DFS import DFS


test_levels: Tuple[str, Union[range, int, None]] = "./json_levels/full_biy_LEVELS.json", None

max_forward_model_calls: int = 500
max_depth: int = 200

if __name__ == "__main__":
    level_set = load_level_set(test_levels[0])
    if test_levels[1] is None:
        test_levels = test_levels[0], range(len(level_set["levels"]))
    if test_levels[1] is int:
        test_levels = test_levels[0], range(test_levels[1], test_levels[1] + 1)
    for i in test_levels[1]:
        print(f"Level Nr.: {i}")
        demo_level_1 = level_set["levels"][i]
        map = parse_map(demo_level_1["ascii"])
        game_state = make_level(map)
        """
        # Choose BFS or DFS
        bfs_agent = BFS()
        solution_bfs = bfs_agent.search(game_state, max_forward_model_calls, max_depth)
        print(f"BFS Solution: {solution_bfs}")

        dfs_agent = DFS()
        solution_dfs = dfs_agent.search(game_state, max_forward_model_calls, max_depth)  # Limit DFS depth to 20
        print(f"DFS Solution: {solution_dfs}")

        a_star_agent = AStar(simple_heuristic)
        solution_a_star = a_star_agent.search(game_state, max_forward_model_calls, max_depth)
        print(f"A* Solution: {solution_a_star}")"""

        heuristics_test_agent = AStar(test_heuristics)
        solution_heuristics_test = heuristics_test_agent.search(game_state, max_forward_model_calls, max_depth)
        print(f"Heuristic Test Solution: {solution_heuristics_test}")