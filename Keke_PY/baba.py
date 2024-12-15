# Baba is Y'all mechanic/rule base
# Version: 2.0py
# Original Code by Milk
# Translated to Python by Descar
import copy
from dataclasses import dataclass
from typing import List, Dict, Union, Optional
from enum import Enum, unique
import pygame

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
    object_map: List[List[List[Union[str, GameObj]]]]
    words: List
    phys: List
    is_connectors: List
    sort_phys: Dict
    rules: List
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
        self.object_map = []
        self.words = []
        self.phys = []
        self.is_connectors = []
        self.sort_phys = {}
        self.rules = []
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
        return self.unique_str()
        #return double_map_to_string(self.obj_map, self.back_map)

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
            return ''.join(map(unique_obj_str, self.object_map[i][j])) + '.'

        return ''.join([
            '\n' if j == -1
                else unique_position_str(i, j)
        for i in range(len(self.object_map))
            for j in range(-1, len(self.object_map[0]))
        ])




def advance_game_state(action: Direction, state: GameState):

    moved_objects = []

    if action != "space":
        move_players(action, moved_objects, state)

    move_auto_movers(moved_objects, state)

    if any(map(is_word, moved_objects)) or any(map(is_key_word, moved_objects)):
        interpret_rules(state)

    state.lazy_evaluation_properties = dict()
    check_win(state)

    return state

def a_can_push_b(
        a: List[Union[GameObj, str]], b: Union[GameObj, str],
        state: GameState,
        objects_to_move_along: List[Union[GameObj, str]],
        already_moved_objs: List[Union[GameObj, str]]
) -> Optional[bool]:
    if b == ' ':
        return True
    if b == '_' or b.is_stopped or b in already_moved_objs:
        return False
    if b.is_movable:
        if b in state.pushables:
            objects_to_move_along.append(b)
            return None
        if b in state.players:
            if all(x in state.players for x in a):
                if all(x.name == b.name for x in a):
                    return True
                else:
                    objects_to_move_along.append(b)
                    return None
        if b.object_type == GameObjectType.Physical:
            return False
        objects_to_move_along.append(b)
        return None
    if not b.is_stopped and not b.is_movable:
        return True
    assert False, "checks should have been exhaustive"


def try_move(e: Union[GameObj, str], action: Direction, state: GameState, already_moved_objs: List[GameObj]) -> bool:

    if e in already_moved_objs:
        return False
    if e == " ":
        return False
    if not e.is_movable:
        return False


    if action not in [Direction.Left, Direction.Right, Direction.Up, Direction.Down]:
        return True
    x_, y_ = e.x, e.y
    current_field_list: List[Union[GameObj, str]] = [e]
    objects_to_move_along: List[Union[GameObj, str]] = []
    while True:
        x_, y_ = x_ + action.dx(), y_ + action.dy()
        if not (0 <= x_ < len(state.object_map[0]) and 0 <= y_ <= len(state.object_map)):
            return False
        objects_in_the_way: List[Union[GameObj, str]] = state.object_map[y_][x_]
        local_objects_to_move_along: List[Union[GameObj, str]] = []
        continue_deeper: bool = False
        for object_in_the_way in objects_in_the_way:
            test: Optional[bool] = a_can_push_b(current_field_list, object_in_the_way, state, local_objects_to_move_along, already_moved_objs)
            if test == False:
                return False
            if test is None:
                continue_deeper = True
        objects_to_move_along += current_field_list
        current_field_list = local_objects_to_move_along
        if not continue_deeper:
            break
    objects_to_move_along += current_field_list

    for object_to_move in reversed(objects_to_move_along):
        state.object_map[object_to_move.y][object_to_move.x].remove(object_to_move)
        object_to_move.x += action.dx()
        object_to_move.y += action.dy()
        state.object_map[object_to_move.y][object_to_move.x].append(object_to_move)
        object_to_move.dir = action
        already_moved_objs.append(object_to_move)

    return True




def move_players(direction: Direction, already_moved_objs: List[GameObj], state: GameState):
    players = state.players
    phys = state.phys
    sort_phys = state.sort_phys
    killers = state.killers
    sinkers = state.sinkers

    for curPlayer in players:
        try_move(curPlayer, direction, state, already_moved_objs)

    destroy_objs(killed(players, killers), state)
    destroy_objs(drowned(phys, sinkers), state)
    destroy_objs(bad_feats(state.featured, sort_phys), state)


def move_auto_movers(already_moved_objs: List[GameObj], state: GameState):
    automovers = state.auto_movers
    players = state.players
    phys = state.phys
    sort_phys = state.sort_phys
    killers = state.killers
    sinkers = state.sinkers

    for curAuto in automovers:
        m = try_move(curAuto, curAuto.dir, state, already_moved_objs)
        if not m:
            # If the mover got stopped, it tries to change direction:
            curAuto.dir = Direction.opposite(curAuto.dir)
            #   TODO: before the line below was added:
            #               Working count: 441
            #                broken count: 20
            #           After it was added:
            #               Working count: 409
            #                broken count: 27
            #              ai fixed count: 25
            #               => insert line
            try_move(curAuto, curAuto.dir, state, already_moved_objs)

    destroy_objs(killed(players, killers), state)
    destroy_objs(drowned(phys, sinkers), state)
    destroy_objs(bad_feats(state.featured, sort_phys), state)


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

    phys = game_state.phys
    words = game_state.words
    sort_phys = game_state.sort_phys
    is_connectors = game_state.is_connectors

    if len(game_state.orig_map) == 0:
        print("ERROR: Map not initialized yet")
        return False

    for r in range(len(game_state.orig_map)):
        for c in range(len(game_state.orig_map[0])):
            character = game_state.orig_map[r][c]
            object_name = character_to_name[character]
            if "_" not in object_name:
                if object_name == "border":
                    game_state.object_map[r][c].append('_')
                    continue
                elif object_name == "empty":
                    continue
                assert False, f"The name '{object_name}' can not be resolved into an object"
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
                game_state.object_map[r][c].append(w)

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
                game_state.object_map[r][c].append(o)




def generate_empty_map(m: List[List[str]]) -> List[List[List[Union[GameObj, str]]]]:
    """
    Split the map into two layers: background map and object map.

    :param m: The input 2D map of characters.
    :return: Tuple (background_map, object_map).
    """
    res: List[List[List[Union[GameObj, str]]]] = []
    for r in range(len(m)):
        res.append([])
        for c in range(len(m[0])):
            res[r].append([])

            #res[r][c].append(m[r][c])

    return res


def only_top_objects_string(game_state: GameState) -> str:
    """
    Convert two 2D maps (object and background) into a combined string representation.

    :param game_state: The current game-state
    :return: A string representation of the combined maps.
    """
    map_string = ""
    for row in range(len(game_state.object_map)):
        for column in range(len(game_state.object_map[0])):
            obj = top_obj_at_pos(column, row, game_state)
            if obj is None:
                map_string += "."
            else:
                map_string += name_to_character[obj.name + ("_word" if is_word(obj) or is_key_word(obj) else "_obj")]
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

    game_state.object_map = generate_empty_map(game_state.orig_map)

    assign_map_objs(game_state)
    interpret_rules(game_state)

    return game_state


def top_obj_at_pos(x: int, y: int, state: GameState) -> Optional[GameObj]:
    """
    Get the object at a specific position in the object map.

    :param x: X coordinate.
    :param y: Y coordinate.
    :param state: The current game-state
    :return: The object at the specified coordinates.
    """
    for obj in reversed(state.object_map[y][x]):
        if obj.__class__ == GameObj:
            return obj
    return None


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


def add_active_rules(word_a: Optional[GameObj], word_b: Optional[GameObj], is_connector: GameObj, rules: List, rule_objs: List):
    """
    Add active rules based on the word objects and their connectors (like "is" in "Baba is You").

    :param word_a: The first word object.
    :param word_b: The second word object.
    :param is_connector: The connector word ("is").
    :param rules: List of current active rules.
    :param rule_objs: List of rule objects in the game.
    """
    if word_a is None or word_b is None:
        return
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
    is_connectors = game_state.is_connectors
    rules = game_state.rules
    rule_objs = game_state.rule_objs
    sort_phys = game_state.sort_phys

    # iterate all is-connectors to identify rules
    for is_connector in is_connectors:
        # Horizontal position
        word_a = top_obj_at_pos(is_connector.x - 1, is_connector.y, game_state)
        word_b = top_obj_at_pos(is_connector.x + 1, is_connector.y, game_state)
        add_active_rules(word_a, word_b, is_connector, rules, rule_objs)

        # Vertical position
        word_c = top_obj_at_pos(is_connector.x, is_connector.y - 1, game_state)
        word_d = top_obj_at_pos(is_connector.x, is_connector.y + 1, game_state)
        add_active_rules(word_c, word_d, is_connector, rules, rule_objs)

    # Interpret sprite changing rules
    transformation(game_state, rules, sort_phys)

    # Reset the objects
    reset_all(game_state)



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


    for p in game_state.phys:
        field = game_state.object_map[p.y][p.x]
        if not p.is_movable and not p.is_stopped:
            game_state.overlaps.append(p)
            # put the object as far down as possible at its position:
            if field[0] != p:
                field.remove(p)
                field.insert(0, p)
        else:
            game_state.unoverlaps.append(p)
            # put the object as far up as possible at its position:
            if field[len(field) - 1] != p:
                field.remove(p)
                field.append(p)

    game_state.unoverlaps.extend(game_state.words)
    # Words will always be as far up as possible:
    for w in game_state.words:
        field = game_state.object_map[w.y][w.x]
        if field[len(field) - 1] != w:
            field.remove(w)
            field.append(w)


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
def killed(players: List[GameObj], killers: List[GameObj]) -> List[GameObj]:
    """
    Check if any player has been killed by a killer object.

    :param players: List of player objects.
    :param killers: List of killer objects.
    :return: List of killed objects.
    """
    dead: List[GameObj] = []
    for player in players:
        for killer in killers:
            if overlapped(player, killer):
                dead += [player, killer]
                # Todo, I assume we can break here
                # TODO: is there a meaning to the comment above?
                #       => break and only delete player
    return dead


# Check if an object has drowned
def drowned(phys: List[GameObj], sinkers: List[GameObj]) -> List[GameObj]:
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
                dead += [p, sinker]
    return dead


# Destroy objects
def destroy_objs(dead, game_state: GameState):
    """
    Remove dead objects (killed or drowned) from the game state.

    :param dead: List of objects to be removed.
    :param game_state: The current game state.
    """
    sort_phys = game_state.sort_phys

    for obj in dead:
        # Remove all reference to the object
        game_state.phys.remove(obj)# = [ x for x in game_state.phys if x != obj ]
        sort_phys[obj.name].remove(obj)# = [ x for x in sort_phys[obj.name] if x != obj ]
        game_state.object_map[obj.y][obj.x].remove(obj)# = [ x for x in game_state.object_map[obj.y][obj.x] if x != obj ]


    # Reset the objects, if anything was deleted
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
def transformation(state: GameState, rules, sort_phys):
    """
    Apply transformation rules (e.g., "Baba is Flag") to change object types in the game state.

    :param state: The current game-state
    :param rules: List of active rules.
    :param sort_phys: Dictionary of sorted physical objects by type.
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
                change_sprite(obj, parts[2], state)


# Changes a sprite from one thing to another
def change_sprite(o, w, state: GameState):
    """
    Change the sprite of a game object to a different type based on rules.

    :param o: Original game object.
    :param w: New object type name.
    :param state: The current game-state
    """
    character = name_to_character[w + "_obj"]
    o2 = GameObj.create_physical_object(w, character, o.x, o.y)
    state.phys.append(o2)  # in with the new...

    # Replace object on obj_map/back_map
    field: List[Union[GameObj, str]] = state.object_map[o.y][o.x]
    field[field.index(o)] = o2

    # Add to the list of objects under a certain name
    if w not in state.sort_phys:
        state.sort_phys[w] = [o2]
    else:
        state.sort_phys[w].append(o2)

    state.phys.remove(o)  # ...out with the old
    state.sort_phys[o.name].remove(o)


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
def bad_feats(featured, sort_phys) -> List[GameObj]:
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
                        baddies += [a, b]

    return baddies


if __name__ == "__main__":
    pass
