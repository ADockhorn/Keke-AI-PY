from typing import Tuple, Union, List, Callable

from Keke_PY.agents.AStar import AStar, simple_heuristic, test_heuristics
from Keke_PY.agents.ai_interface import AIInterface
from Keke_PY.baba import Direction
from Keke_PY.simulation import load_level_set, parse_map, make_level
from BFS import BFS
from DFS import DFS


test_levels: Tuple[str, Union[range, int, None]] = "./json_levels/full_biy_LEVELS.json", range(6, 20)

max_forward_model_calls: Union[int, None] = None
max_depth: Union[int, None] = 200


agent_generators: List[Tuple[str, Callable[[], AIInterface]]] = [
    #("BFS", BFS),
    #("DFS", DFS),
    #("A*(simple)", lambda: AStar(simple_heuristic)),
    ("A*(0*heuristics)", lambda: AStar(test_heuristics)),
]

if __name__ == "__main__":
    level_set = load_level_set(test_levels[0])
    if test_levels[1] is None:
        test_levels = test_levels[0], range(len(level_set["levels"]))
    if test_levels[1].__class__ == int:
        test_levels = test_levels[0], range(test_levels[1], test_levels[1] + 1)
    for i in test_levels[1]:
        print(f"Level Nr.: {i}")
        demo_level_1 = level_set["levels"][i]
        map = parse_map(demo_level_1["ascii"])
        game_state = make_level(map)

        for name, get_agent in agent_generators:
            print(f"Now running: {name}")
            agent = get_agent()
            solution = agent.search(game_state, max_forward_model_calls, max_depth)
            print(f"{name} Solution: {solution}\n\n")

