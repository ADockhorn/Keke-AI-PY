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


def interpret_solution(solution: str):
    map_solution = {
        "s": Direction.Wait,
        "r": Direction.Right,
        "l": Direction.Left,
        "u": Direction.Up,
        "d": Direction.Down,
    }
    return [map_solution[s.lower()] for s in solution]


if __name__ == "__main__":
    import random
    import time

    level_set = load_level_set("json_levels/full_biy_LEVELS.json")
    #level_set = load_level_set("json_levels/demo_LEVELS.json")
    #level_set = load_level_set("json_levels/search_biy_LEVELS.json")
    errors = 0
    for level_id, level in enumerate(level_set["levels"]):
        game_map = parse_map(level["ascii"])
        solution = interpret_solution(level["solution"])
        game_state = make_level(game_map)

        # test if the given solution works
        for i, action in enumerate(solution):
            game_state = advance_game_state(action, game_state)

            if check_win(game_state):
                break
        else:
            #print(map_to_string(game_map))
            #print(game_state)
            #print(solution)
            errors += 1
            print("given solution not working", level["id"], errors, level_id, "".join([s.value for s in solution]))

