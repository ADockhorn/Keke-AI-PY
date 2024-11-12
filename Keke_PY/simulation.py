# Baba is Y'all mechanic/rule base
# Version: 2.0py
# Original Code by Milk
# Translated to Python by Descar

from Keke_PY.baba import *
import json


def load_level_set(filename_of_level_set):
    with open(filename_of_level_set, 'r') as f:
        level_set = json.load(f)
    return level_set


def execute_level():
    pass


def execute_level_set():
    pass


if __name__ == "__main__":
    import random
    import time

    level_set = load_level_set("json_levels/demo_LEVELS.json")

    demo_level_1 = level_set["levels"][2]
    game_map = parse_map(demo_level_1["ascii"])
    print(map_to_string(game_map))

    game_state = make_level(game_map)

    # ai agent
    directions = [Direction.Right, Direction.Down, Direction.Up, Direction.Left, Direction.Wait]
    start = time.time()
    for i in range(3500):
        action = random.choice(directions)
        game_state = advance_game_state(action, game_state)

    end = time.time()
    print("time", end-start)

