import time
from typing import Tuple, Union, Iterable

from PIL.ImageOps import solarize

from Keke_PY.baba import GameState, Direction, imgHash, advance_game_state, parse_map, make_level
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
            elif char in "Ww_ ":
                yield Direction.Wait
            else:
                return


test_levels: Tuple[str, Union[range, int, None]] = "./json_levels/full_biy_LEVELS.json", None


if __name__ == '__main__':
    from simulation import load_level_set
    level_set = load_level_set(test_levels[0])
    if test_levels[1] is None:
        test_levels = test_levels[0], range(len(level_set["levels"]))
    if test_levels[1].__class__ == int:
        test_levels = test_levels[0], range(test_levels[1], test_levels[1] + 1)
    for i in test_levels[1]:
        print(f"Currently playing Level Nr.: {i}")
        demo_level_1 = level_set["levels"][i]
        print(demo_level_1["solution"])


        if not play_level(demo_level_1["ascii"], yield_solution_delayed(demo_level_1["solution"])):
            while not play_level(demo_level_1["ascii"], inputs_from_keyboard()):
                play_level(demo_level_1["ascii"], yield_solution_delayed(demo_level_1["solution"], 1.0))