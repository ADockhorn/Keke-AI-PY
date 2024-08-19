import pygame
import sys
from baba import *
import json
from dataclasses import dataclass
from pygame.locals import *


def load_level_set(filename_of_level_set):
    with open(filename_of_level_set, 'r') as f:
        level_set = json.load(f)
    return level_set


def execute_level():
    pass


def execute_level_set():
    pass


def make_level(map):
    game_state = GameState()
    clear_level(game_state)
    set_level(game_state, map)
    return game_state


# initialize the saved level
def set_level(game_state: GameState, map: List[List[str]]):
    game_state.orig_map = map

    maps = split_map(game_state.orig_map)
    game_state.back_map = maps[0]
    game_state.obj_map = maps[1]

    assign_map_objs(game_state)
    interpret_rules(game_state)

    endRules = []
    initRules = game_state.rules

    aiControl = False
    moved = False
    unsolvable = False

    saveLevel = False

    moveSteps = []

    wonGame = False
    alreadySolved = False


# get the rules that are currently active
def get_current_rules(game_state):
    return game_state.rules


TILE_SIZE = 48


def render_tile(tile, xpos, ypos):
    if isinstance(tile, str):
        screen.blit(imgHash[tile], (xpos, ypos))
    else:
        screen.blit(tile.img, (xpos, ypos))

def render_gamestate(game_state: GameState):
    background = game_state.back_map
    objects = game_state.obj_map

    for y, row in enumerate(background):
        for x, tile in enumerate(row):
            # Calculate position for the tile
            xpos = x * TILE_SIZE
            ypos = y * TILE_SIZE

            # Draw background tile
            render_tile(tile, xpos, ypos)

            # Draw object map overlay
            object_tile = objects[y][x]
            if object_tile != " ":
                render_tile(object_tile, xpos, ypos)


# Example function to update the display
def update_display(game_state: GameState):
    screen.fill((0, 0, 0))  # Clear screen with black
    render_gamestate(game_state)
    pygame.display.flip()  # Update the display


def advance_game_state(action: Direction, state: GameState):
    moved_objects = []

    if action != "space":
        move_players(action, moved_objects, state)

    move_auto_movers(moved_objects, state)

    for moved_object in moved_objects:
        if is_word(moved_object):
            interpret_rules(state)

    won_game = win(state.players, state.winnables)
    return {"next_state": state, "won": won_game}


def canMove(e: GameObj, action: Direction,
            om: List[List[Union[str, GameObj]]], bm: List[List[Union[str, GameObj]]],
            movedObjs: List, p, u, phys, sort_phys):
    if e in movedObjs:
        return False

    if e == " ":
        return False
    if not e.is_movable:
        return False

    o = ' '

    if action == Direction.Up:
        if e.y - 1 < 0:
            return False
        if bm[e.y - 1][e.x] == '_':
            return False
        o = om[e.y - 1][e.x]
    elif action == Direction.Down:
        if e.y + 1 >= len(bm):
            return False
        if bm[e.y + 1][e.x] == '_':
            return False
        o = om[e.y + 1][e.x]
    elif action == Direction.Left:
        if e.x - 1 < 0:
            return False
        if bm[e.y][e.x - 1] == '_':
            return False
        o = om[e.y][e.x - 1]
    elif action == Direction.Right:
        if e.x + 1 >= len(bm[0]):
            return False
        if bm[e.y][e.x + 1] == '_':
            return False
        o = om[e.y][e.x + 1]

    if o == ' ':
        return True
    if o.is_stopped:
        return False
    if o.is_movable:
        if o in u:
            return move_obj(o, action, om, bm, movedObjs, p, u, phys, sort_phys)
        elif o in p and e not in p:
            return True
        elif o.object_type == GameObjectType.Physical and (len(u) == 0 or o not in u):
            return False
        elif ((e.is_movable or o.is_movable) and e.object_type == GameObjectType.Physical and
              o.object_type == GameObjectType.Physical):
            return True
        elif e.name == o.name and e in p and is_phys(o) and is_phys(e):
            return move_obj_merge(o, action, om, bm, movedObjs, p, u, phys, sort_phys)
        else:
            return move_obj(o, action, om, bm, movedObjs, p, u, phys, sort_phys)

    if not o.is_stopped and not o.is_movable:
        return True

    return True


def move_obj(o: GameObj, dir: Direction,
             om: List[List[Union[str, GameObj]]], bm: List[List[Union[str, GameObj]]],
             movedObjs: List, p, u, phys, sort_phys):
    if canMove(o, dir, om, bm, movedObjs, p, u, phys, sort_phys):
        om[o.y][o.x] = ' '
        if dir == Direction.Up:
            o.y -= 1
        elif dir == Direction.Down:
            o.y += 1
        elif dir == Direction.Left:
            o.x -= 1
        elif dir == Direction.Right:
            o.x += 1
        om[o.y][o.x] = o
        movedObjs.append(o)
        o.dir = dir
        return True
    else:
        return False


def move_obj_merge(o: GameObj, dir: Direction,
                   om: List[List[Union[str, GameObj]]], bm: List[List[Union[str, GameObj]]],
                   movedObjs: List, p, u, phys: List, sort_phys: Dict):
    if canMove(o, dir, om, bm, movedObjs, p, u, phys, sort_phys):
        om[o.y][o.x] = ' '
        if dir == Direction.Up:
            o.y -= 1
        elif dir == Direction.Down:
            o.y += 1
        elif dir == Direction.Left:
            o.x -= 1
        elif dir == Direction.Right:
            o.x += 1
        om[o.y][o.x] = o
        movedObjs.append(o)
        o.dir = dir
        return True
    else:
        om[o.y][o.x] = ' '
        # Code for additional logic as per the JavaScript function
        return True


def move_players(dir: Direction, mo: List, state: GameState):
    om = state.obj_map
    bm = state.back_map
    players = state.players
    pushs = state.pushables
    phys = state.phys
    sort_phys = state.sort_phys
    killers = state.killers
    sinkers = state.sinkers
    featured = state.featured

    for curPlayer in players:
        move_obj(curPlayer, dir, om, bm, mo, players, pushs, phys, sort_phys)

    destroy_objs(killed(players, killers), state)
    destroy_objs(drowned(phys, sinkers), state)
    destroy_objs(bad_feats(featured, sort_phys), state)


def move_auto_movers(mo: List, state: GameState):
    automovers = state.auto_movers
    om = state.obj_map
    bm = state.back_map
    players = state.players
    pushs = state.pushables
    phys = state.phys
    sort_phys = state.sort_phys
    killers = state.killers
    sinkers = state.sinkers
    featured = state.featured

    for curAuto in automovers:
        m = move_obj(curAuto, curAuto.dir, om, bm, mo, players, pushs, phys, sort_phys)
        if not m:
            curAuto.dir = Direction.opposite(curAuto.dir) # walk towards the opposite direction

    destroy_objs(killed(players, killers), state)
    destroy_objs(drowned(phys, sinkers), state)
    destroy_objs(bad_feats(featured, sort_phys), state)


if __name__ == "__main__":
    import random
    import time
    import copy

    level_set = load_level_set("../../Keke_JS/json_levels/demo_LEVELS.json")

    demo_level_1 = level_set["levels"][0]
    map = parse_map(demo_level_1["ascii"])
    print(show_map(map))

    game_state = make_level(map)

    """
    directions = [Direction.Right, Direction.Down, Direction.Up, Direction.Left, Direction.Wait]
    start = time.time()
    for i in range(3500):
        action = random.choice(directions)
        result = advance_game_state(action, game_state)
        game_state = result["next_state"]

    end = time.time()
    print("time", end-start)
    """

    WIDTH, HEIGHT = len(map[0])*TILE_SIZE, len(map)*TILE_SIZE
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Keke is You Py')

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                action = None
                if event.key == K_w:
                    action = Direction.Up
                elif event.key == K_a:
                    action = Direction.Left
                elif event.key == K_s:
                    action = Direction.Down
                elif event.key == K_d:
                    action = Direction.Right
                elif event.key == K_SPACE:
                    action = Direction.Wait
                else:
                    continue

                if action is not None:
                    result = advance_game_state(action, game_state)
                    game_state = result["next_state"]
                    running = not result["won"]
                    pass

        update_display(game_state)
