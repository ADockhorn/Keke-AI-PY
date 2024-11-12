from Keke_PY.simulation import load_level_set, parse_map, make_level
from BFS import BFS
from DFS import DFS


if __name__ == "__main__":
    level_set = load_level_set("../../Keke_JS/json_levels/demo_LEVELS.json")
    demo_level_1 = level_set["levels"][0]
    map = parse_map(demo_level_1["ascii"])
    game_state = make_level(map)

    # Choose BFS or DFS
    bfs_agent = BFS()
    solution_bfs = bfs_agent.search(game_state)
    print(f"BFS Solution: {solution_bfs}")

    dfs_agent = DFS()
    solution_dfs = dfs_agent.search(game_state, max_depth=20)  # Limit DFS depth to 20
    print(f"DFS Solution: {solution_dfs}")
