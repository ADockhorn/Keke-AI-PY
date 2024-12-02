import time
from itertools import chain
from operator import concat
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
        if True:
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


def inputs_from_keyboard(mem_buffer: List[Direction] = []) -> Iterable[Direction]:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == K_w or event.key == K_UP:
                    mem_buffer += [Direction.Up]
                    yield Direction.Up
                elif event.key == K_a or event.key == K_LEFT:
                    mem_buffer += [Direction.Left]
                    yield Direction.Left
                elif event.key == K_s or event.key == K_DOWN:
                    mem_buffer += [Direction.Down]
                    yield Direction.Down
                elif event.key == K_d or event.key == K_RIGHT:
                    mem_buffer += [Direction.Right]
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
            elif char in "SsWw":
                yield Direction.Wait
            else:
                return


working_levels: List[Tuple[str, Union[range, int, None, Iterable[int]]]] = [
    (
        "./json_levels/demo_LEVELS.json",
        [i for i in range(14) if i not in []]
    ), (
        "./json_levels/full_biy_LEVELS.json",
        [i for i in range(184) if i not in []] # 183?!?
    ), (
        "./json_levels/search_biy_LEVELS.json",
        [i for i in range(62) if i not in []]
    ), (
        "./json_levels/test_LEVELS.json",
        [i for i in range(0, 134) if i not in []]
    ), (
        "./json_levels/train_LEVELS.json",
        [i for i in range(50) if i not in []]
    ), (
        "./json_levels/user_milk_biy_LEVELS.json",
        [i for i in range(17) if i not in []]
    )
]

broken_levels: List[Tuple[str, Union[range, int, None, Iterable[int]]]] = [
    (
        "./json_levels/demo_LEVELS.json",
        []
    ), (
        "./json_levels/full_biy_LEVELS.json",
        []
    ), (
        "./json_levels/search_biy_LEVELS.json",
        []
    ), (
        "./json_levels/test_LEVELS.json",
        []
    ), (
        "./json_levels/train_LEVELS.json",
        []
    ), (
        "./json_levels/user_milk_biy_LEVELS.json",
        []
    )
]

test = working_levels

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


    if False:
        play_level(load_level_set(
            "./json_levels/full_biy_LEVELS.json"
        )["levels"][5]["ascii"], yield_solution_delayed(
            "UUUULLLLLUULUUUUUUUURU", 0.5
        ))


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
                    working.append((file_name, i))
                    continue
                ai_solution = try_ai(
                    demo_level_1["ascii"],
                    0,#5 ** (len(demo_level_1["solution"]) + 2),
                    len(demo_level_1["solution"]) + 2
                )
                if ai_solution is not None:
                    play_level(demo_level_1["ascii"], yield_solution_delayed(ai_solution, 0.5))
                    ai_fixed.append((file_name, i, ai_solution))

                    for name, index, solution in ai_fixed:
                        print(f"{name}\t{index}\t: {solution}\n")
                    input("Waiting...:")
                    continue
                while True:#int(input("Try?")):
                    key_buffer: List[Direction] = []
                    play_level(demo_level_1["ascii"], chain(
                        #yield_solution_delayed(demo_level_1["solution"], 0.5),
                        inputs_from_keyboard(key_buffer)
                    ))
                    key_str: str = ""
                    for direction in key_buffer:
                        key_str += direction.name[0]
                    print(key_str)


                broken.append((file_name, i))

    print(f"Working count: {len(working)}\n broken count: {len(broken)}")

    for name, index, solution in ai_fixed:
        print(f"{name}\t{index}\t: {solution}\n")





"""

./json_levels/full_biy_LEVELS.json	9	: DLDULLLDRRRURRDULDUL => DLLDULDLDRRRUUUL

./json_levels/full_biy_LEVELS.json	19	: DDLLRUUUUUUURUULDRDLLRDDDLULURDRUUURULLRDDDDDDDL => UDLUURULLLRD

./json_levels/full_biy_LEVELS.json  23  : rlrrllllrrrllrrdrrrrrrdlllllllllllluuluulddllluuurdrrrrrrrddddddddlllllurrrrrrrrrrruddlllluuddrrrruu =>
                                          RRRRDDDDLULDRDLLLLRRUULDULDU

./json_levels/full_biy_LEVELS.json  27  : dlldlllurrrururdrdlllluldrrrruuurdddrrullddddllldlllurdruddldluuurrrrrrrluuuuuuurrdluddduuuldddddddd =>
                                          DDLLLLLURRRRURDRDLLLLULDRRRRUUURDDDDDDDDLLLLLDLUUURDRURRRRUUUURRULULDDDDDDDDDDDDDR

./json_levels/full_biy_LEVELS.json  32  : rrludl => RDDDDR

./json_levels/full_biy_LEVELS.json  63  : rullluldsssud => RULLLULDRLRLRD

./json_levels/full_biy_LEVELS.json  70  : rdddddddrddudlulruuruuulruululrddddrrruuludldluuu => LLDDDDDDDDDRLD

./json_levels/full_biy_LEVELS.json  183 : llddrdrrrudlllluururrrurrdduulllllddrrrrrrrsllluuuuuuuuuuuuuuu =>
                                          RRRRDRULURURRDDRDLDDDDLLLUULLLLLLLDRRRRRRRDRULURDDRUDRRULDLUUUUUUULLLLLLLLDDDDRRRUUUU

./json_levels/search_biy_LEVELS.json    20  : rullluldsssud => RULLLULDUUUUUD

./json_levels/search_biy_LEVELS.json    24  : rdddddddrddudlulruuruuulruululrddddrrruuludldluuu => LLDDDDDDDDDRLD

./json_levels/search_biy_LEVELS.json    61  : llddrdrrrudlllluururrrurrdduulllllddrrrrrrrsllluuuuuuuuuuuuuuu =>
                                              RRRRDRULURURRDDRDLDDDDLLLUULLLLLLLDRRRRRRRDRULURDDRUDRRULDLUUUUUUULLLLLLLLDDDDRRRUUUU

./json_levels/test_LEVELS.json      4   : DLDULLLDRRRURRDULDUL => LLDDULDLDRRRUUUL

./json_levels/test_LEVELS.json      13  : DDLLRUUUUUUURUULDRDLLRDDDLULURDRUUURULLRDDDDDDDL => UDLUURULLLRD

./json_levels/test_LEVELS.json      17  : rlrrllllrrrllrrdrrrrrrdlllllllllllluuluulddllluuurdrrrrrrrddddddddlllllurrrrrrrrrrruddlllluuddrrrruu =>
                                          RRRRDDDDLULDRDLLLLRRUULDULDU

./json_levels/test_LEVELS.json      18  : dlldlllurrrururdrdlllluldrrrruuurdddrrullddddllldlllurdruddldluuurrrrrrrluuuuuuurrdluddduuuldddddddd =>
                                          DDLLLLLURRRRURDRDLLLLULDRRRRUUURDDDDDDDDLLLLLDLUUURDRURRRRUUUURRULULDDDDDDDDDDDDDR

./json_levels/test_LEVELS.json      22  : rrludl => RDDDDR

./json_levels/test_LEVELS.json      46  : rullluldsssud => RULLLULDUUUUUD

./json_levels/test_LEVELS.json      51  : rdddddddrddudlulruuruuulruululrddddrrruuludldluuu => LLDDDDDDDDDRLD

./json_levels/test_LEVELS.json      133 : llddrdrrrudlllluururrrurrdduulllllddrrrrrrrsllluuuuuuuuuuuuuuu
                                          RRRRDRULURURRDDRDLDDDDLLLUULLLLLLLDRRRRRRRDRULURDDRUDRRULDLUUUUUUULLLLLLLLDDDDRRRUUUU

./json_levels/user_milk_biy_LEVELS.json     5   : DDLLRUUUUUUURUULDRDLLRDDDLULURDRUUURULLRDDDDDDDL => UDLUURULLLRD


"""