import time
from itertools import chain
from typing import Tuple, Union, Iterable, List, Optional

from PIL.ImageOps import solarize

from Keke_PY.agents.AStar import AStar, simple_heuristic
from Keke_PY.baba import GameState, Direction, imgHash, advance_game_state, parse_map, make_level
from Keke_PY.agents.BFS import BFS


from pygame.locals import *
import pygame

TILE_SIZE = 48


def render_tile(screen, tile, xpos, ypos):
    if isinstance(tile, str):
        screen.blit(imgHash[tile], (xpos, ypos))
    else:
        screen.blit(imgHash[tile.img], (xpos, ypos))


def render_game_state(screen, game_state: GameState):
    background = game_state.back_map
    objects = game_state.obj_map

    for y, row in enumerate(background):
        for x, tile in enumerate(row):
            # Calculate position for the tile
            x_pos = x * TILE_SIZE
            y_pos = y * TILE_SIZE

            # Draw background tile
            render_tile(screen, tile, x_pos, y_pos)

            # Draw object map overlay
            object_tile = objects[y][x]
            if object_tile != " ":
                render_tile(screen, object_tile, x_pos, y_pos)


# Example function to update the display
def update_display(screen, game_state: GameState):
    screen.fill((0, 0, 0))  # Clear screen with black
    render_game_state(screen, game_state)
    pygame.display.flip()  # Update the display


def play_level(ascii_map, action_source: Iterable[Direction]) -> bool:
    game_map = parse_map(ascii_map)
    game_state = make_level(game_map)
    return play_game(game_state, action_source)


def play_game(initial_game_state: GameState, action_source: Iterable[Direction]) -> bool:
    # human agent
    width, height = len(initial_game_state.orig_map[0]) * TILE_SIZE, len(initial_game_state.orig_map) * TILE_SIZE
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Keke is You Py')

    # Main loop
    game_state = initial_game_state
    update_display(screen, game_state)
    for action in action_source:
        game_state = advance_game_state(action, game_state)
        update_display(screen, game_state)

        # TODO: remove these lines:
        if False:
            for back in game_state.back_map:
                print(back)
            for obj in game_state.obj_map:
                print(obj)
            print(game_state.unique_str())



        if game_state.lazy_evaluation_properties["win"]:
            break


    if "win" in game_state.lazy_evaluation_properties and game_state.lazy_evaluation_properties["win"]:
        print("<<<SOLVED>>>")
        return True
    else:
        print("!!!NOT SOLVED!!!")
        return False


def inputs_from_keyboard() -> Iterable[Direction]:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == K_w or event.key == K_UP:
                    yield Direction.Up
                elif event.key == K_a or event.key == K_LEFT:
                    yield Direction.Left
                elif event.key == K_s or event.key == K_DOWN:
                    yield Direction.Down
                elif event.key == K_d or event.key == K_RIGHT:
                    yield Direction.Right
                elif event.key == K_SPACE:
                    yield Direction.Wait

def yield_solution_delayed(solution: str, delay: float = 0.0) -> Iterable[Direction]:
    start_time = time.time()
    index = 1
    iterator = iter(solution)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        if time.time() > start_time + delay * index:
            index += 1
            try:
                char = next(iterator)
            except StopIteration:
                return
            if char in "Uu":
                yield Direction.Up
            elif char in "Ll":
                yield Direction.Left
            elif char in "Dd":
                yield Direction.Down
            elif char in "Rr":
                yield Direction.Right
            elif char in "Ss":
                yield Direction.Wait
            else:
                return


working_levels: List[Tuple[str, Union[range, int, None, Iterable[int]]]] = [
    (
        "./json_levels/demo_LEVELS.json",
        [i for i in range(14) if i not in []]
    ), (
        "./json_levels/full_biy_LEVELS.json",
        [i for i in range(184) if i not in [9, 19, 23, 27, 32, 63, 70, 183]] # 183?!?
    ), (
        "./json_levels/search_biy_LEVELS.json",
        [i for i in range(62) if i not in [20, 24, 61]]
    ), (
        "./json_levels/test_LEVELS.json",
        [i for i in range(0, 134) if i not in [4, 13, 17, 18, 22, 46, 51, 133]]
    ), (
        "./json_levels/train_LEVELS.json",
        [i for i in range(50) if i not in []]
    ), (
        "./json_levels/user_milk_biy_LEVELS.json",
        [i for i in range(17) if i not in [5]]
    )
]

broken_levels: List[Tuple[str, Union[range, int, None, Iterable[int]]]] = [
    (
        "./json_levels/demo_LEVELS.json",
        []
    ), (
        "./json_levels/full_biy_LEVELS.json",
        [9, 19, 23, 27, 32, 63, 70, 183] # 183?!?
    ), (
        "./json_levels/search_biy_LEVELS.json",
        [20, 24, 61]
    ), (
        "./json_levels/test_LEVELS.json",
        [4, 13, 17, 18, 22, 46, 51, 133]
    ), (
        "./json_levels/train_LEVELS.json",
        []
    ), (
        "./json_levels/user_milk_biy_LEVELS.json",
        [5]
    )
]

test = working_levels + broken_levels

def try_ai(level, max_forward_model_calls: Union[int, None] = 50, max_depth: Union[int, None] = 50) -> Optional[str]:
    ai_solution_attempt = AStar(simple_heuristic).search(make_level(parse_map(level)), max_forward_model_calls, max_depth)
    if ai_solution_attempt[0] is not None:
        print(ai_solution_attempt[0])
        solution_str = ""
        for d in ai_solution_attempt[0]:
            solution_str += d[0]
        return solution_str
    else:
        return None

if __name__ == '__main__':
    from simulation import load_level_set
    working: List[Tuple[str, int]] = []
    broken: List[Tuple[str, int]] = []
    ai_fixed: List[Tuple[str, int, str]] = []
    for file_name, level_nrs in test:
        level_set = load_level_set(file_name)
        if level_nrs is None:
            level_nrs = range(len(level_set["levels"]))
        if level_nrs.__class__ == int:
            level_nrs = range(level_nrs, level_nrs + 1)
        for i in level_nrs:
            print(f"Currently playing '{file_name}' Level Nr.: {i}")
            demo_level_1 = level_set["levels"][i]
            print(demo_level_1["solution"])

            if False:
                play_level(demo_level_1["ascii"], inputs_from_keyboard())
            else:

                if play_level(demo_level_1["ascii"], yield_solution_delayed(demo_level_1["solution"])):
                    working += [(file_name, i)]
                    continue
                ai_solution = try_ai(demo_level_1["ascii"], 10000, len(demo_level_1["solution"]) + 2)
                if ai_solution is not None:
                    play_level(demo_level_1["ascii"], yield_solution_delayed(ai_solution, 0.5))
                    ai_fixed += [(file_name, i, ai_solution)]
                    continue
                # TODO: insert manual solution input
                broken += [(file_name, i)]

    print(f"Working count: {len(working)}\n broken count: {len(broken)}")

    for name, index, solution in ai_fixed:
        print(f"{name}\t{i}\t: {solution}\n")






"""Working count: 409
 broken count: 27
./json_levels/full_biy_LEVELS.json	5	: URRRULUUUUUR

./json_levels/full_biy_LEVELS.json	5	: UUDWUDUURDWLLLDDDDRUUURRRRRR

./json_levels/full_biy_LEVELS.json	5	: LLULULUUUUU

./json_levels/full_biy_LEVELS.json	5	: UUUULLLLLUULUUUUUUUURU

./json_levels/full_biy_LEVELS.json	5	: UUUUUUURRRRUURRU

./json_levels/full_biy_LEVELS.json	5	: DDDDDDDDDDDDDDDD

./json_levels/full_biy_LEVELS.json	5	: DDRDDLLDDD

./json_levels/search_biy_LEVELS.json	5	: URRRULUUUUUR

./json_levels/search_biy_LEVELS.json	5	: LLULULUUUUU

./json_levels/search_biy_LEVELS.json	5	: UUUULLLLLUULUUUUUUUURU

./json_levels/search_biy_LEVELS.json	5	: DDDDDDDDDDDDDDDD

./json_levels/search_biy_LEVELS.json	5	: DDRDDLLDDD

./json_levels/test_LEVELS.json	5	: UUDWUDUURDWLLLDDDDRUUURRRRRR

./json_levels/test_LEVELS.json	5	: UUUUUUURRRRUURRU

./json_levels/test_LEVELS.json	5	: DDDDDDDDDDDDDDDD

./json_levels/test_LEVELS.json	5	: DDRDDLLDDD

./json_levels/train_LEVELS.json	5	: URRRULUUUUUR

./json_levels/train_LEVELS.json	5	: LLULULUUUUU

./json_levels/train_LEVELS.json	5	: UUUULLLLLUULUUUUUUUURU

./json_levels/user_milk_biy_LEVELS.json	5	: URRRULUUUUUR

./json_levels/full_biy_LEVELS.json	5	: DDRDDR

./json_levels/full_biy_LEVELS.json	5	: URRDDRDR

./json_levels/search_biy_LEVELS.json	5	: URRDDRDR

./json_levels/test_LEVELS.json	5	: DDRDDR

./json_levels/test_LEVELS.json	5	: URRDDRDR


Process finished with exit code 0
"""