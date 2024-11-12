from Keke_PY.baba import GameState, Direction, imgHash, advance_game_state, parse_map, make_level, check_win
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


def play_level(ascii_map):
    game_map = parse_map(ascii_map)
    game_state = make_level(game_map)
    play_game(game_state)


def play_game(initial_game_state: GameState):
    # human agent
    width, height = len(initial_game_state.orig_map[0]) * TILE_SIZE, len(initial_game_state.orig_map) * TILE_SIZE
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Keke is You Py')

    # Main loop
    game_state = initial_game_state
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                action = None
                if event.key == K_w or event.key == K_UP:
                    action = Direction.Up
                elif event.key == K_a or event.key == K_LEFT:
                    action = Direction.Left
                elif event.key == K_s or event.key == K_DOWN:
                    action = Direction.Down
                elif event.key == K_d or event.key == K_RIGHT:
                    action = Direction.Right
                elif event.key == K_SPACE:
                    action = Direction.Wait
                else:
                    continue

                if action is not None:
                    result = advance_game_state(action, game_state)
                    game_state = result
                    running = not check_win(game_state)
                    pass

        update_display(screen, game_state)


if __name__ == '__main__':
    from simulation import load_level_set
    level_set = load_level_set("json_levels/demo_LEVELS.json")
    demo_level_1 = level_set["levels"][9]
    print(demo_level_1["id"])
    play_level(demo_level_1["ascii"])
