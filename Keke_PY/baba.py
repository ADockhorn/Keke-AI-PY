# Baba is Y'all mechanic/rule base
# Version: 2.0py
# Original Code by Milk
# Translated to Python by Descar
import copy
from dataclasses import dataclass
from typing import List, Dict, Union
from enum import Enum
import pygame
from copy import deepcopy

# Assign ASCII values to images
character_to_name = {
    '_': "border",
    ' ': "empty",
    # '.': "empty",
    'b': "baba_obj",
    'B': "baba_word",
    '1': "is_word",
    '2': "you_word",
    '3': "win_word",
    's': "skull_obj",
    'S': "skull_word",
    'f': "flag_obj",
    'F': "flag_word",
    'o': "floor_obj",
    'O': "floor_word",
    'a': "grass_obj",
    'A': "grass_word",
    '4': "kill_word",
    'l': "lava_obj",
    'L': "lava_word",
    '5': "push_word",
    'r': "rock_obj",
    'R': "rock_word",
    '6': "stop_word",
    'w': "wall_obj",
    'W': "wall_word",
    '7': "move_word",
    '8': "hot_word",
    '9': "melt_word",
    'k': "keke_obj",
    'K': "keke_word",
    'g': "goop_obj",
    'G': "goop_word",
    '0': "sink_word",
    'v': "love_obj",
    'V': "love_word",
}

name_to_character = {y: x for x, y in character_to_name.items()}


def make_img_hash():
    """
    Create a dictionary that maps ASCII characters to their respective images.

    :return: Dictionary where keys are characters and values are Pygame image surfaces.
    """
    img_hash = {}
    all_chars = character_to_name.keys()

    for c in all_chars:
        # Check if image is already assigned to character
        if c not in img_hash:
            img = pygame.image.load("img/" + character_to_name[c] + ".png")
            img_hash[c] = img
    return img_hash


imgHash = make_img_hash()


features = ["hot", "melt", "open", "shut", "move"]
featPairs = [["hot", "melt"], ["open", "shut"]]



class Direction(Enum):
    Left = 1
    Right = 2
    Up = 3
    Down = 4
    Wait = 5
    Undefined = 5

    @classmethod
    def _missing_(cls, value):
        return cls.Undefined

    @staticmethod
    def opposite(value):
        if value == Direction.Left:
            return Direction.Right
        if value == Direction.Right:
            return Direction.Left
        if value == Direction.Up:
            return Direction.Down
        if value == Direction.Down:
            return Direction.Up
        else:
            return Direction.Undefined

    def dx(self) -> int:
        if self == Direction.Left:
            return -1
        if self == Direction.Right:
            return 1
        else:
            return 0
    def dy(self) -> int:
        if self == Direction.Up:
            return -1
        if self == Direction.Down:
            return 1
        else:
            return 0


class GameObjectType(Enum):
    Physical = 1
    Word = 2
    Keyword = 3
    Undefined = 4

    @classmethod
    def _missing_(cls, value):
        return cls.Undefined


@dataclass
class GameObj:
    object_type: GameObjectType
    name: str
    x: int
    y: int
    img: str
    obj: str            # only used for word objects
    is_movable: bool
    is_stopped: bool
    feature: str        # only used for physical objects
    dir: Direction      # only used for physical object

    def __init__(self, name, img, x, y,
                 object_type=GameObjectType.Undefined, obj="", is_movable=False, is_stopped=False):
        self.name = name
        self.x = x
        self.y = y
        self.img = img
        self.object_type = object_type

        self.is_movable = is_movable
        self.is_stopped = is_stopped

        # physical object feature
        self.feature = ""
        self.dir = Direction.Undefined

        # word object feature
        self.obj = obj

    @classmethod
    def create_physical_object(cls, name, img_character, x, y):
        return cls(name, img_character, x, y, object_type=GameObjectType.Physical)

    @classmethod
    def create_word_object(cls, name, img_character, obj, x, y):
        return cls(name, img_character, x, y, obj=obj, object_type=GameObjectType.Word, is_movable=True)

    @classmethod
    def create_keyword_object(cls, name, img_character, obj, x, y):
        return cls(name, img_character, x, y, obj=obj, object_type=GameObjectType.Keyword, is_movable=True)


@dataclass
class GameState:
    orig_map: List
    obj_map: List[List[Union[str, GameObj]]]
    back_map: List[List[Union[str, GameObj]]]
    words: List
    phys: List
    is_connectors: List
    sort_phys: Dict
    rules: List
    # TODO@ask: having this here isn't sound with respect to the idea of equivalent states :(
    all_seen_rules: set
    rule_objs: List
    players: List
    auto_movers: List
    winnables: List
    pushables: List
    killers: List
    sinkers: List
    featured: Dict
    overlaps: List
    unoverlaps: List
    lazy_evaluation_properties: Dict

    def __init__(self):
        self.clear()

    def clear(self):
        self.orig_map = []
        self.obj_map = []
        self.back_map = []
        self.words = []
        self.phys = []
        self.is_connectors = []
        self.sort_phys = {}
        self.rules = []
        self.all_seen_rules = set()
        self.rule_objs = []
        self.players = []
        self.auto_movers = []
        self.winnables = []
        self.pushables = []
        self.killers = []
        self.sinkers = []
        self.featured = {}
        self.overlaps = []
        self.unoverlaps = []
        self.lazy_evaluation_properties = dict()

    def copy(self):
        new_game_state = copy.deepcopy(self)
        new_game_state.lazy_evaluation_properties = dict()
        return new_game_state

    def __str__(self):
        return double_map_to_string(self.obj_map, self.back_map)

    # TODO@ask: I can never guarantee, this string is unique, without ALWAYS checking EVERYTHING in here. :(
    # TODO@ask: For this to work, "TODO@ask: maybe just switch obj_map and ob" (ll. 927) needs to be fixed.
    # TODO@ask: For this to work, "move_obj_merge" might be changed to either be the same as "move_obj", or delete the Game-Object entirely.
    def unique_str(self) -> str:

        def unique_obj_str(obj: Union[GameObj, str]) -> str:
            if obj.__class__ == str:
                return obj
            if obj.__class__ == GameObj:
                return name_to_character[obj.name + (
                    "_word" if is_word(obj) or is_key_word(obj)
                    else "_obj"
                )] + str(obj.dir.value)

        def unique_position_str(i: int, j: int) -> str:
            back = self.back_map[i][j]
            obj = self.obj_map[i][j]
            if back == " " and obj == " ":
                return "."
            else:
                return unique_obj_str(back) + unique_obj_str(obj)

        return ''.join([
            '\n' if j == -1
                else unique_position_str(i, j)
        for i in range(len(self.obj_map))
            for j in range(-1, len(self.obj_map[0]))
        ])




def advance_game_state(action: Direction, state: GameState):

    # TODO: Copy and give reference to child
    #  TODO@ask: The above TODO should not be done, if states should be able to be independent of how they are reached.
    moved_objects = []

    if action != "space":
        move_players(action, moved_objects, state)

    move_auto_movers(moved_objects, state)

    if any(map(is_word, moved_objects)) or any(map(is_key_word, moved_objects)):
        interpret_rules(state)

    state.lazy_evaluation_properties = dict()
    check_win(state)

    return state


def can_move(e: Union[GameObj, str], action: Direction, state: GameState, moved_objs: List[GameObj]) -> bool:
    if e in moved_objs:
        return False

    if e == " ":
        return False
    if not e.is_movable:
        return False


    if action not in [Direction.Left, Direction.Right, Direction.Up, Direction.Down]:
        return True
    x_, y_ = e.x + action.dx(), e.y + action.dy()
    if not (0 <= x_ < len(state.back_map[0]) and 0 <= y_ <= len(state.back_map)):
        return False
    if state.back_map[y_][x_] == '_':
        return False
    o = state.obj_map[y_][x_]


    if o == ' ':
        return True
    if o.is_stopped:
        return False
    if o.is_movable:
        # TODO@ask: does this make sense?
        if o in state.pushables:
            return move_obj(o, action, state, moved_objs)
        # TODO@ask: what is the line below supposed to do?
        if o in state.players:
            if e in state.players:
                if e.name == o.name:
                    # TODO@ask: doesn't the next 2 lines prevent player merging / moving in unison?
                    if o.object_type == GameObjectType.Physical:
                        return False
                    return move_obj_merge(o, action, state, moved_objs)
                else:
                    #TODO@ask: could we also merge player characters of different type?
                    move_obj(o, action, state, moved_objs)
            else:
                return True
        # TODO@ask: can't non-player objects merge?
        if o.object_type == GameObjectType.Physical:
            return False #TODO@ask: why is this False??
        return move_obj(o, action, state, moved_objs)

    if not o.is_stopped and not o.is_movable:
        return True

    assert False, "checks should have been exhaustive"


def move_obj(o: GameObj, direction: Direction, state: GameState, moved_objs: List[GameObj]) -> bool:
    if can_move(o, direction, state, moved_objs):
        state.obj_map[o.y][o.x] = ' '
        o.x += direction.dx()
        o.y += direction.dy()
        state.obj_map[o.y][o.x] = o
        moved_objs.append(o)
        o.dir = direction
        return True
    else:
        return False


def move_obj_merge(o: GameObj, direction: Direction, state: GameState, moved_objs: List[GameObj]) -> bool:
    if can_move(o, direction, state, moved_objs):
        state.obj_map[o.y][o.x] = ' '
        o.x += direction.dx()
        o.y += direction.dy()
        state.obj_map[o.y][o.x] = o
        moved_objs.append(o)
        o.dir = direction
        return True
    else:
        state.obj_map[o.y][o.x] = ' '
        # Code for additional logic as per the JavaScript function
        return True


def move_players(direction: Direction, moved_objs: List[GameObj], state: GameState):
    players = state.players
    phys = state.phys
    sort_phys = state.sort_phys
    killers = state.killers
    sinkers = state.sinkers
    featured = state.featured

    for curPlayer in players:
        move_obj(curPlayer, direction, state, moved_objs)

    destroy_objs(killed(players, killers), state)
    destroy_objs(drowned(phys, sinkers), state)
    destroy_objs(bad_feats(featured, sort_phys), state)


def move_auto_movers(moved_objs: List[GameObj], state: GameState):
    automovers = state.auto_movers
    players = state.players
    phys = state.phys
    sort_phys = state.sort_phys
    killers = state.killers
    sinkers = state.sinkers
    featured = state.featured

    for curAuto in automovers:
        m = move_obj(curAuto, curAuto.dir, state, moved_objs)
        if not m:
            # If the mover got stopped, it tries to change direction:
            curAuto.dir = Direction.opposite(curAuto.dir)
            #   TODO@ask: before the line below was added:
            #               Working count: 441
            #                broken count: 20
            #           After it was added:
            #               Working count: 409
            #                broken count: 27
            #              ai fixed count: 25
            #move_obj(curAuto, curAuto.dir, state, moved_objs)

    destroy_objs(killed(players, killers), state)
    destroy_objs(drowned(phys, sinkers), state)
    destroy_objs(bad_feats(featured, sort_phys), state)


def assign_map_objs(game_state: GameState):
    """
    Populate the game state with objects from the object map.
    Objects can be physical (like "baba") or word-based (like "Baba is You").

    :param game_state: Current game state.
    :return: Boolean indicating success or failure.
    """
    game_state.sort_phys = {}
    game_state.phys = []
    game_state.words = []
    game_state.is_connectors = []

    game_map = game_state.obj_map
    phys = game_state.phys
    words = game_state.words
    sort_phys = game_state.sort_phys
    is_connectors = game_state.is_connectors

    if len(game_map) == 0:
        print("ERROR: Map not initialized yet")
        return False

    for r in range(len(game_map)):
        for c in range(len(game_map[0])):
            character = game_map[r][c]
            object_name = character_to_name[character]
            if "_" not in object_name:
                continue
            base_obj, word_type = object_name.split("_")

            # retrieve word-based objects
            if word_type == "word":
                if base_obj + "_obj" not in name_to_character:
                    # create keyword object
                    w = GameObj.create_keyword_object(base_obj, character, None, c, r)
                else:
                    w = GameObj.create_word_object(base_obj, character, None, c, r)

                # keep track of special key-words
                words.append(w)
                if base_obj == "is":
                    is_connectors.append(w)

                # replace character with object
                game_map[r][c] = w

            # retrieve physical-based objects
            elif word_type == "obj":
                # create object
                o = GameObj.create_physical_object(base_obj, character, c, r)

                # keep track of objects
                phys.append(o)
                if base_obj not in sort_phys:
                    sort_phys[base_obj] = []
                sort_phys[base_obj].append(o)

                # replace character with object
                game_map[r][c] = o


def init_empty_map(m):
    """
    Initialize an empty map based on the dimensions of the input map.

    :param m: The input map for which an empty map will be created.
    :return: A 2D list representing an empty map.
    """
    new_map = []
    for r in range(len(m)):
        new_row = []
        for c in range(len(m[0])):
            new_row.append(' ')

        new_map.append(new_row)
    return new_map


def split_map(m):
    """
    Split the map into two layers: background map and object map.

    :param m: The input 2D map of characters.
    :return: Tuple (background_map, object_map).
    """
    background_map = init_empty_map(m)
    object_map = init_empty_map(m)
    for r in range(len(m)):
        for c in range(len(m[0])):
            map_character = m[r][c]
            parts = character_to_name[map_character].split("_")

            # background
            if len(parts) == 1:
                background_map[r][c] = map_character
                object_map[r][c] = ' '
            # object
            else:
                background_map[r][c] = ' '
                object_map[r][c] = map_character

    return background_map, object_map


def double_map_to_string(object_map: List[List[Union[str, GameObj]]], background_map: List[List[Union[str, GameObj]]]):
    """
    Convert two 2D maps (object and background) into a combined string representation.

    :param object_map: A 2D list representing the object map.
    :param background_map: A 2D list representing the background map.
    :return: A string representation of the combined maps.
    """
    map_string = ""
    for row in range(len(object_map)):
        for column in range(len(object_map[0])):
            game_object = object_map[row][column]
            background = background_map[row][column]
            if row == 0 or column == 0 or row == len(object_map)-1 or column == len(object_map[0])-1:
                map_string += "_"
            elif game_object == " " and background == " ":
                map_string += "."
            elif game_object == " ":
                map_string += name_to_character[background.name + ("_word" if is_word(background) or is_key_word(background) else "_obj")] # TODO@ask: check this line change
            else:
                map_string += name_to_character[game_object.name + ("_word" if is_word(game_object) or is_key_word(game_object) else "_obj")]
        map_string += "\n"
    map_string = map_string.rstrip("\n")  # Remove the trailing newline
    return map_string


def map_to_string(game_map: List[List[str]]):
    """
    Generate a printable version of the map by converting it into a comma-separated string.

    :param game_map: A 2D list representing the game map.
    :return: A string representing the map.
    """
    map_arr = []
    for r in range(len(game_map)):
        row = ""
        for c in range(len(game_map[r])):
            row += game_map[r][c]
        map_arr.append(row)

    map_str = ""
    for row in map_arr:
        map_str += ",".join(row) + "\n"

    return map_str


# turns a string object back into a 2d array
def parse_map(map_string: str) -> List[List[str]]:
    """
    Parse a string into a 2D map.

    :param map_string: A string representing the map (e.g., '.' for empty, characters for objects).
    :return: A 2D list representing the parsed map.
    """
    new_map = []
    rows = map_string.split("\n")
    for row in rows:
        row = row.replace(".", " ")
        new_map.append(list(row))
    return new_map


def parse_map_wh(ms: str, w: int, h: int) -> List[List[str]]:
    """
    Parse a string map into a 2D list with specific width and height.

    :param ms: A string representation of the map.
    :param w: Width of the map.
    :param h: Height of the map.
    :return: A 2D list representing the parsed map.
    """
    new_map = []
    for r in range(h):
        row = ms[(r*w):(r*w) + w].replace(".", " ")
        new_map.append(list(row))
    return new_map


def make_level(game_map: List[List[str]]) -> GameState:
    game_state = GameState()
    clear_level(game_state)

    game_state.orig_map = game_map

    maps = split_map(game_state.orig_map)
    game_state.back_map = maps[0]
    game_state.obj_map = maps[1]

    assign_map_objs(game_state)
    interpret_rules(game_state)

    return game_state


def obj_at_pos(x: int, y: int, om: List[List[GameObj]]):
    """
    Get the object at a specific position in the object map.

    :param x: X coordinate.
    :param y: Y coordinate.
    :param om: The object map (2D list).
    :return: The object at the specified coordinates.
    """
    try:
        return om[y][x]
    except:
        print("blub")
    return om[y][x]


def is_word(e: Union[str, GameObj]):
    """
    Check if a given object is a word.

    :param e: The object or string to check.
    :return: True if the object is a word, False otherwise.
    """
    if isinstance(e, str):
        return False
    return e.object_type == GameObjectType.Word


def is_key_word(e: Union[str, GameObj]):
    """
    Check if a given object is a keyword (a word that doesn't have a corresponding object)
    e.g. is, win, melt, ...

    :param e: The object or string to check.
    :return: True if the object is a word, False otherwise.
    """
    if isinstance(e, str):
        return False
    return e.object_type == GameObjectType.Keyword


def is_phys(e: Union[str, GameObj]):
    """
    Check if a given object is a physical object.

    :param e: The object or string to check.
    :return: True if the object is a physical object, False otherwise.
    """
    if isinstance(e, str):
        return False
    return e.object_type == GameObjectType.Physical


def add_active_rules(word_a: GameObj, word_b: GameObj, is_connector: GameObj, rules: List, rule_objs: List):
    """
    Add active rules based on the word objects and their connectors (like "is" in "Baba is You").

    :param word_a: The first word object.
    :param word_b: The second word object.
    :param is_connector: The connector word ("is").
    :param rules: List of current active rules.
    :param rule_objs: List of rule objects in the game.
    """
    if (is_word(word_a) and not is_key_word(word_a)) and (is_word(word_b) or is_key_word(word_b)):
        # Add a new rule if not already made
        r = f"{word_a.name}-{is_connector.name}-{word_b.name}"
        if r not in rules:
            rules.append(r)

        # Add as a rule object
        rule_objs.append(word_a)
        rule_objs.append(is_connector)
        rule_objs.append(word_b)


def interpret_rules(game_state: GameState):
    """
    Interpret and apply the rules based on the current game state and the words in the map.

    :param game_state: The current game state.
    """
    # Reset the rules (since a word object was changed)
    game_state.rules = []
    game_state.rule_objs = []

    # Get all relevant fields
    om = game_state.obj_map
    bm = game_state.back_map
    is_connectors = game_state.is_connectors
    rules = game_state.rules
    rule_objs = game_state.rule_objs
    sort_phys = game_state.sort_phys
    phys = game_state.phys

    # iterate all is-connectors to identify rules
    for is_connector in is_connectors:
        # Horizontal position
        word_a = obj_at_pos(is_connector.x - 1, is_connector.y, om)
        word_b = obj_at_pos(is_connector.x + 1, is_connector.y, om)
        add_active_rules(word_a, word_b, is_connector, rules, rule_objs)

        # Vertical position
        word_c = obj_at_pos(is_connector.x, is_connector.y - 1, om)
        word_d = obj_at_pos(is_connector.x, is_connector.y + 1, om)
        add_active_rules(word_c, word_d, is_connector, rules, rule_objs)

    # Interpret sprite changing rules
    transformation(om, bm, rules, sort_phys, phys)

    # Reset the objects
    reset_all(game_state)

    # add all new rules to all_seen_rules
    game_state.all_seen_rules |= set(game_state.rules)


# Check if array contains string with a substring
def has(arr: List, ss: str):
    """
    Check if any item in the list contains a specific substring.

    :param arr: List of strings.
    :param ss: Substring to search for.
    :return: True if any string in the list contains the substring, False otherwise.
    """
    for item in arr:
        if ss in item:
            return True
    return False


def clear_level(game_state):
    """
    Clear the current level by resetting the game state.

    :param game_state: The current game state.
    """
    game_state.clear()


# Function resetAll
def reset_all(game_state: GameState):
    """
    Reset all object properties and reapply rules in the current game state.

    :param game_state: The current game state.
    """
    # Reset the objects
    reset_obj_props(game_state.phys)
    set_players(game_state)
    set_auto_movers(game_state)
    set_wins(game_state)
    set_pushes(game_state)
    set_stops(game_state)
    set_kills(game_state)
    set_sinks(game_state)
    set_overlaps(game_state)
    set_features(game_state)


# Set the player objects
def set_players(game_state: GameState):
    """
    Set the player objects based on the "you" rule.

    :param game_state: The current game state.
    """
    players = game_state.players
    rules = game_state.rules
    sort_phys = game_state.sort_phys

    players.clear()
    for rule in rules:
        if "you" in rule:
            players.extend(sort_phys.get(rule.split("-")[0], []))

    # Make all the players movable
    for player in players:
        player.is_movable = True


def set_auto_movers(game_state: GameState):
    """
    Set the automatically moving objects based on the "move" rule.

    :param game_state: The current game state.
    """
    game_state.auto_movers = []
    auto_movers = game_state.auto_movers
    rules = game_state.rules
    sort_phys = game_state.sort_phys

    for rule in rules:
        if "move" in rule:
            auto_movers.extend(sort_phys.get(rule.split("-")[0], []))

    # Make all the NPCs movable and set default direction
    for auto_mover in auto_movers:
        auto_mover.is_movable = True
        if auto_mover.dir == Direction.Undefined:
            auto_mover.dir = Direction.Right


# Set the winning objects
def set_wins(game_state: GameState):
    """
    Set the winnable objects based on the "win" rule.

    :param game_state: The current game state.
    """
    game_state.winnables = []
    winnables = game_state.winnables
    rules = game_state.rules
    sort_phys = game_state.sort_phys

    for rule in rules:
        if "win" in rule:
            winnables.extend(sort_phys.get(rule.split("-")[0], []))


# Set the pushable objects
def set_pushes(game_state: GameState):
    """
    Set the pushable objects based on the "push" rule.

    :param game_state: The current game state.
    """
    game_state.pushables = []
    pushables = game_state.pushables
    rules = game_state.rules
    sort_phys = game_state.sort_phys

    for rule in rules:
        if "push" in rule:
            pushables.extend(sort_phys.get(rule.split("-")[0], []))

    # Make all the pushables movable
    for pushable in pushables:
        pushable.is_movable = True


# Set the stopping objects
def set_stops(game_state: GameState):
    """
    Set the stopping objects based on the "stop" rule.

    :param game_state: The current game state.
    """
    game_state.stoppables = []
    stoppables = game_state.stoppables
    rules = game_state.rules
    sort_phys = game_state.sort_phys

    for rule in rules:
        if "stop" in rule:
            stoppables.extend(sort_phys.get(rule.split("-")[0], []))

    # Make all the stoppables stopped
    for stoppable in stoppables:
        stoppable.is_stopped = True


# Set the killable objects
def set_kills(game_state: GameState):
    """
    Set the killable objects based on the "kill" rule.

    :param game_state: The current game state.
    """
    game_state.killers = []
    killers = game_state.killers
    rules = game_state.rules
    sort_phys = game_state.sort_phys

    for rule in rules:
        if "kill" in rule or "sink" in rule:
            killers.extend(sort_phys.get(rule.split("-")[0], []))


# Set the sinkable objects
def set_sinks(game_state: GameState):
    """
    Set the sinkable objects based on the "sink" rule.

    :param game_state: The current game state.
    """
    game_state.sinkers = []
    sinkers = game_state.sinkers
    rules = game_state.rules
    sort_phys = game_state.sort_phys

    for rule in rules:
        if "sink" in rule:
            sinkers.extend(sort_phys.get(rule.split("-")[0], []))


# Set objects that are unmovable but not stoppable
def set_overlaps(game_state: GameState):
    """
    Set the objects that can overlap and remove the ones that can't.

    :param game_state: The current game state.
    """
    game_state.overlaps = []
    game_state.unoverlaps = []

    bm = game_state.back_map
    om = game_state.obj_map
    overlaps = game_state.overlaps
    unoverlaps = game_state.unoverlaps
    phys = game_state.phys
    words = game_state.words

    for p in phys:
        if not p.is_movable and not p.is_stopped:
            overlaps.append(p)
            if om[p.y][p.x] == p:
                # TODO@ask: i now just switch obj_map and back_map, if necessary, instead of making the obj_map[y][x] = ' '
                om[p.y][p.x] = bm[p.y][p.x]
                bm[p.y][p.x] = p
        else:
            unoverlaps.append(p)
            if bm[p.y][p.x] == p:
                # TODO@ask: i now just switch obj_map and back_map, if necessary, instead of making the back_map[y][x] = ' '
                bm[p.y][p.x] = om[p.y][p.x]
                om[p.y][p.x] = p

    unoverlaps.extend(words)
    # Words will always be in the object layer
    for w in words:
        om[w.y][w.x] = w


# Check if an object is overlapping another
def overlapped(a: GameObj, b: GameObj):
    """
    Check if two game objects overlap.

    :param a: First game object.
    :param b: Second game object.
    :return: True if the objects overlap, False otherwise.
    """
    return a == b or (a.x == b.x and a.y == b.y)


# Reset all the properties of every object
def reset_obj_props(phys: List[GameObj]):
    """
    Reset the properties of physical objects.

    :param phys: List of physical game objects.
    """
    for p in phys:
        p.is_movable = False
        p.is_stopped = False
        p.feature = ""


# Check if the player has stepped on a kill object
def killed(players, killers):
    """
    Check if any player has been killed by a killer object.

    :param players: List of player objects.
    :param killers: List of killer objects.
    :return: List of killed objects.
    """
    dead = []
    for player in players:
        for killer in killers:
            if overlapped(player, killer):
                dead.append([player, killer])
                # Todo, I assume we can break here
                # TODO@ask: is there a meaning to the comment above?
    return dead


# Check if an object has drowned
def drowned(phys, sinkers):
    """
    Check if any objects have drowned by falling into sinkers.

    :param phys: List of physical objects.
    :param sinkers: List of sinker objects.
    :return: List of drowned objects.
    """
    dead = []
    for p in phys:
        for sinker in sinkers:
            if p != sinker and overlapped(p, sinker):
                dead.append([p, sinker])
    return dead


# Destroy objects
def destroy_objs(dead, game_state: GameState):
    """
    Remove dead objects (killed or drowned) from the game state.

    :param dead: List of objects to be removed.
    :param game_state: The current game state.
    """
    bm = game_state.back_map
    om = game_state.obj_map
    phys = game_state.phys
    sort_phys = game_state.sort_phys

    for p, o in dead:
        # Remove reference of the player and the murder object
        phys = [ x for x in phys if x not in [o, p] ]
        sort_phys[p.name] = [ x for x in sort_phys[p.name] if x != p ]
        if o != p:
            sort_phys[o.name] = [ x for x in sort_phys[o.name] if x != o ]

        # Clear the space
        bm[o.y][o.x] = ' '
        om[p.y][p.x] = ' '

    # Reset the objects
    if dead:
        reset_all(game_state)


# Check if the player has entered a win state
def check_win(game_state: GameState) -> bool:
    """
    Check if any player object has reached a winning state.

    :param game_state: The current game state.
    :return: True if the game has been won, False otherwise.
    """
    if "win" not in game_state.lazy_evaluation_properties:
        for player in game_state.players:
            for winnable in game_state.winnables:
                if overlapped(player, winnable):
                    game_state.lazy_evaluation_properties["win"] = True
                    return True
        else:
            game_state.lazy_evaluation_properties["win"] = False
    return game_state.lazy_evaluation_properties["win"]


def is_obj_word(w: str):
    """
    Check if a given word string represents a word object in the game.

    :param w: Word string.
    :return: True if it's a word object, False otherwise.
    """
    if w+"_obj" in name_to_character:
        return True


# Turns all of one object type into all of another object type
def transformation(om, bm, rules, sort_phys, phys):
    """
    Apply transformation rules (e.g., "Baba is Flag") to change object types in the game state.

    :param om: Object map.
    :param bm: Background map.
    :param rules: List of active rules.
    :param sort_phys: Dictionary of sorted physical objects by type.
    :param phys: List of physical objects.
    """
    # x-is-x takes priority and makes it immutable
    x_is_x = []
    for rule in rules:
        parts = rule.split("-")
        if parts[0] == parts[2] and parts[0] in sort_phys:
            x_is_x.append(parts[0])

    # Transform sprites (x-is-y == x becomes y)
    for rule in rules:
        parts = rule.split("-")
        if parts[0] not in x_is_x and is_obj_word(parts[0]) and is_obj_word(parts[2]):
            all_objs = sort_phys.get(parts[0], []).copy()
            for obj in all_objs:
                change_sprite(obj, parts[2], om, bm, phys, sort_phys)


# Changes a sprite from one thing to another
def change_sprite(o, w, om, bm, phys, sort_phys):
    """
    Change the sprite of a game object to a different type based on rules.

    :param o: Original game object.
    :param w: New object type name.
    :param om: Object map.
    :param bm: Background map.
    :param phys: List of physical objects.
    :param sort_phys: Dictionary of sorted physical objects by type.
    """
    character = name_to_character[w + "_obj"]
    o2 = GameObj.create_physical_object(w, character, o.x, o.y)
    phys.append(o2)  # in with the new...

    # Replace object on obj_map/back_map
    if obj_at_pos(o.x, o.y, om) == o:
        om[o.y][o.x] = o2
    else:
        bm[o.y][o.x] = o2

    # Add to the list of objects under a certain name
    if w not in sort_phys:
        sort_phys[w] = [o2]
    else:
        sort_phys[w].append(o2)

    phys.remove(o)  # ...out with the old
    sort_phys[o.name].remove(o)


# Adds a feature to word groups based on ruleset
def set_features(game_state: GameState):
    """
    Set features (e.g., "hot", "melt") on objects based on the rules in the game state.

    :param game_state: The current game state
    """
    game_state.featured = {}
    featured = game_state.featured
    rules = game_state.rules
    sort_phys = game_state.sort_phys

    # Add a feature to the sprites (x-is-y == x has y feature)
    for rule in rules:
        parts = rule.split("-")
        # Add a feature to a sprite set
        if parts[2] in features and parts[0] not in features and parts[0] in sort_phys:
            # No feature set yet so make a new array
            if parts[2] not in featured:
                featured[parts[2]] = [parts[0]]
            else:
                # Or append it
                featured[parts[2]].append(parts[0])

            # Set the physical objects' features
            ps = sort_phys[parts[0]]
            for p in ps:
                p.feature = parts[2]


# Similar to killed() check if feat pairs are overlapped and destroy both
def bad_feats(featured, sort_phys):
    baddies = []

    for pair in featPairs:
        # Check if both features have object sets
        if pair[0] in featured and pair[1] in featured:
            # Get all the sprites for each group
            a_set = []
            b_set = []

            for feature in featured[pair[0]]:
                a_set.extend(sort_phys[feature])

            for feature in featured[pair[1]]:
                b_set.extend(sort_phys[feature])

            # Check for overlaps between objects
            for a in a_set:
                for b in b_set:
                    if overlapped(a, b):
                        baddies.append([a, b])

    return baddies


if __name__ == "__main__":
    pass
