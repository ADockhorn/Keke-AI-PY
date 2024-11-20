from typing import Tuple

from Keke_PY.agents.AStar import AStar, simple_heuristic, test_heuristics
from Keke_PY.simulation import load_level_set, parse_map, make_level
from BFS import BFS
from DFS import DFS


test_level: Tuple[str, int] = "./json_levels/demo_LEVELS.json", 9

max_forward_model_calls: int = 500
max_depth: int = 200

if __name__ == "__main__":
    level_set = load_level_set(test_level[0])
    demo_level_1 = level_set["levels"][test_level[1]]
    map = parse_map(demo_level_1["ascii"])
    game_state = make_level(map)

    # Choose BFS or DFS
    bfs_agent = BFS()
    solution_bfs = bfs_agent.search(game_state, max_forward_model_calls, max_depth)
    print(f"BFS Solution: {solution_bfs}")

    dfs_agent = DFS()
    solution_dfs = dfs_agent.search(game_state, max_forward_model_calls, max_depth)  # Limit DFS depth to 20
    print(f"DFS Solution: {solution_dfs}")

    a_star_agent = AStar(simple_heuristic)
    solution_a_star = a_star_agent.search(game_state, max_forward_model_calls, max_depth)
    print(f"A* Solution: {solution_a_star}")

    heuristics_test_agent = AStar(test_heuristics)
    solution_heuristics_test = heuristics_test_agent.search(game_state, max_forward_model_calls, max_depth)
    print(f"Heuristic Test Solution: {solution_heuristics_test}")