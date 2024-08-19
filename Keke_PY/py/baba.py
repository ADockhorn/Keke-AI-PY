# Baba is Y'all mechanic/rule base
# Version: 2.0py
# Original Code by Milk
# Translated by Descar

from demo_levels import demoLevels, demoLevelChromos
from dataclasses import dataclass
from PIL import Image
from typing import List, Dict, Union
from enum import Enum
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
    img_hash = {}
    all_chars = character_to_name.keys()

    for c in all_chars:
        # Check if image is already assigned to character
        if c not in img_hash:
            img = pygame.image.load("../../Keke_JS/img/" + character_to_name[c] + ".png")
            img_hash[c] = img
    return img_hash


imgHash = make_img_hash()


features = ["hot", "melt", "open", "shut", "move"]
featPairs = [["hot", "melt"], ["open", "shut"]]

oppDir = {
    "left":    "right",
    "right":   "left",
    "up":      "down",
    "down":    "up",
}


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


class GameObjectType(Enum):
    Physical = 1
    Word = 2
    Undefined = 3

    @classmethod
    def _missing_(cls, value):
        return cls.Undefined


@dataclass
class GameObj:
    object_type: GameObjectType
    name: str
    x: int
    y: int
    img: pygame.surface.Surface
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
    def create_physical_object(cls, name, img, x, y):
        return cls(name, img, x, y, object_type=GameObjectType.Physical)

    @classmethod
    def create_word_object(cls, name, img, obj, x, y):
        return cls(name, img, x, y, obj=obj, object_type=GameObjectType.Word, is_movable=True)


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



def assign_map_objs(game_state: GameState):
    game_state.sort_phys = {}
    game_state.phys = []
    game_state.words = []
    game_state.is_connectors = []

    map = game_state.obj_map
    phys = game_state.phys
    words = game_state.words
    sort_phys = game_state.sort_phys
    is_connectors = game_state.is_connectors

    if len(map) == 0:
        print("ERROR: Map not initialized yet")
        return False

    for r in range(len(map)):
        for c in range(len(map[0])):
            character = map[r][c]
            object_name = character_to_name[character]
            if "_" not in object_name:
                continue
            base_obj, word_type = object_name.split("_")

            # retrieve word-based objects
            if word_type == "word":
                # create object
                w = GameObj.create_word_object(base_obj, imgHash[character], None, c, r)

                # keep track of special key-words
                words.append(w)
                if base_obj == "is":
                    is_connectors.append(w)

                # replace character with object
                map[r][c] = w

            # retrieve physical-based objects
            elif word_type == "obj":
                # create object
                o = GameObj.create_physical_object(base_obj, imgHash[character], c, r)

                # keep track of objects
                phys.append(o)
                if base_obj not in sort_phys:
                    sort_phys[base_obj] = []
                sort_phys[base_obj].append(o)

                # replace character with object
                map[r][c] = o


def init_empty_map(m):
    new_map = []
    for r in range(len(m)):
        new_row = []
        for c in range(len(m[0])):
            new_row.append(' ')

        new_map.append(new_row)
    return new_map


# populates 2 separate maps (background map and object pos map)
def split_map(m):
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


def map_to_str(map: List[List[str]]) -> str:
    str = ""
    for row in map:
        for object in row:
            if object != " ":
                str += object
            else:
                str += "."
        str += "\n"
    str = str.rstrip("\n")  # Remove the trailing newline
    return str


def doubleMap2Str(object_map: List[List[Union[str, GameObj]]], background_map: List[List[Union[str, GameObj]]]):
    map_string = ""
    for row in range(len(object_map)):
        for column in range(len(object_map[0])):
            object = object_map[row][column]
            background = background_map[row][column]
            if row == 0 or column == 0 or row == len(object_map)-1 or column == len(object_map[0])-1:
                map_string += "_"
            elif object == " " and background == " ":
                map_string += "."
            elif object == " ":
                map_string += name_to_character[background.name + ("_word" if is_word(background) else "_obj")]
            else:
                map_string += name_to_character[object.name + ("_word" if is_word(object) else "_obj")]
        map_string += "\n"
    map_string = map_string.rstrip("\n")  # Remove the trailing newline
    return map_string


def show_map(map: List[List[str]]):
    map_arr = []
    for r in range(len(map)):
        row = ""
        for c in range(len(map[r])):
            row += map[r][c]
        map_arr.append(row)

    map_str = ""
    for row in map_arr:
        map_str += ",".join(row) + "\n"

    return map_str


# turns a string object back into a 2d array
def parse_map(map_string: str) -> List[List[str]]:
    new_map = []
    rows = map_string.split("\n")
    for row in rows:
        row = row.replace(".", " ")
        new_map.append(list(row))
    return new_map


def parse_map_wh(ms: str, w: int, h: int) -> List[List[str]]:
    new_map = []
    for r in range(h):
        row = ms[(r*w):(r*w) + w].replace(".", " ")
        new_map.append(list(row))
    return new_map


def obj_at_pos(x: int, y: int, om: List[List[GameObj]]):
    return om[y][x]


def is_word(e: Union[str, GameObj]):
    if isinstance(e, str):
        return False
    return e.object_type == GameObjectType.Word


def is_phys(e: Union[str, GameObj]):
    if isinstance(e, str):
        return False
    return e.object_type == GameObjectType.Physical


def add_active_rules(word_a: GameObj, word_b: GameObj, is_connector: GameObj, rules: List, rule_objs: List):
    if is_word(word_a) and is_word(word_b):
        # Add a new rule if not already made
        r = f"{word_a.name}-{is_connector.name}-{word_b.name}"
        if r not in rules:
            rules.append(r)

        # Add as a rule object
        rule_objs.append(word_a)
        rule_objs.append(is_connector)
        rule_objs.append(word_b)


def interpret_rules(game_state: GameState):

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


# Check if array contains string with a substring
def has(arr: List, ss: str):
    for item in arr:
        if ss in item:
            return True
    return False


def clear_level(game_state):
    game_state.clear()


# Function resetAll
def reset_all(game_state: GameState):
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
    players = game_state.players
    rules = game_state.rules
    sort_phys = game_state.sort_phys

    players.clear()
    for rule in rules:
        if "you" in rule:
            players.extend(sort_phys[rule.split("-")[0]])

    # Make all the players movable
    for player in players:
        player.is_movable = True



# Set the autonomously moving objects
def set_auto_movers(game_state: GameState):
    game_state.auto_movers = []
    auto_movers = game_state.auto_movers
    rules = game_state.rules
    sort_phys = game_state.sort_phys

    for rule in rules:
        if "move" in rule:
            auto_movers.extend(sort_phys[rule.split("-")[0]])

    # Make all the NPCs movable and set default direction
    for auto_mover in auto_movers:
        auto_mover.is_movable = True
        if auto_mover.dir == Direction.Undefined:
            auto_mover.dir = Direction.Right


# Set the winning objects
def set_wins(game_state: GameState):
    game_state.winnables = []
    winnables = game_state.winnables
    rules = game_state.rules
    sort_phys = game_state.sort_phys

    for rule in rules:
        if "win" in rule:
            keyword = rule.split("-")[0]
            if keyword in sort_phys:
                winnables.extend(sort_phys[keyword])


# Set the pushable objects
def set_pushes(game_state: GameState):
    game_state.pushables = []
    pushables = game_state.pushables
    rules = game_state.rules
    sort_phys = game_state.sort_phys

    for rule in rules:
        if "push" in rule:
            pushables.extend(sort_phys[rule.split("-")[0]])

    # Make all the pushables movable
    for pushable in pushables:
        pushable.is_movable = True


# Set the stopping objects
def set_stops(game_state: GameState):
    game_state.stoppables = []
    stoppables = game_state.stoppables
    rules = game_state.rules
    sort_phys = game_state.sort_phys

    for rule in rules:
        if "stop" in rule:
            stoppables.extend(sort_phys[rule.split("-")[0]])

    # Make all the stoppables stopped
    for stoppable in stoppables:
        stoppable.is_stopped = True


# Set the killable objects
def set_kills(game_state: GameState):
    game_state.killers = []
    killers = game_state.killers
    rules = game_state.rules
    sort_phys = game_state.sort_phys

    for rule in rules:
        if "kill" in rule or "sink" in rule:
            killers.extend(sort_phys[rule.split("-")[0]])


# Set the sinkable objects
def set_sinks(game_state: GameState):
    game_state.sinkers = []
    sinkers = game_state.sinkers
    rules = game_state.rules
    sort_phys = game_state.sort_phys

    for rule in rules:
        if "sink" in rule:
            sinkers.extend(sort_phys[rule.split("-")[0]])


# Set objects that are unmovable but not stoppable
def set_overlaps(game_state: GameState):
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
            bm[p.y][p.x] = p
            om[p.y][p.x] = ' '
        else:
            unoverlaps.append(p)
            om[p.y][p.x] = p
            bm[p.y][p.x] = ' '

    unoverlaps.extend(words)
    # Words will always be in the object layer
    for w in words:
        om[w.y][w.x] = w


# Check if an object is overlapping another
def overlapped(a: GameObj, b: GameObj):
    return a == b or (a.x == b.x and a.y == b.y)


# Reset all the properties of every object
def reset_obj_props(phys: List[GameObj]):
    for p in phys:
        p.is_movable = False
        p.is_stopped = False
        p.feature = ""


# Check if the player has stepped on a kill object
def killed(players, killers):
    dead = []
    for player in players:
        for killer in killers:
            if overlapped(player, killer):
                dead.append([player, killer])
                # Todo, I assume we can break here
    return dead


# Check if an object has drowned
def drowned(phys, sinkers):
    dead = []
    for p in phys:
        for sinker in sinkers:
            if p != sinker and overlapped(p, sinker):
                dead.append([p, sinker])
    return dead


# Destroy objects
def destroy_objs(dead, game_state: GameState):
    bm = game_state.back_map
    om = game_state.obj_map
    phys = game_state.phys
    sort_phys = game_state.sort_phys

    for p, o in dead:
        # Remove reference of the player and the murder object
        phys.remove(p)
        phys.remove(o)
        sort_phys[p.name].remove(p)
        sort_phys[o.name].remove(o)

        # Clear the space
        bm[o.y][o.x] = ' '
        om[p.y][p.x] = ' '

    # Reset the objects
    if dead:
        reset_all(game_state)


# Check if the player has entered a win state
def win(players: List, winnables: List):
    for player in players:
        for winnable in winnables:
            if overlapped(player, winnable):
                return True
    return False

def is_obj_word(w: str):
    if w+"_obj" in name_to_character:
        return True

# Turns all of one object type into all of another object type
def transformation(om, bm, rules, sort_phys, phys):
    # x-is-x takes priority and makes it immutable
    xisx = []
    for rule in rules:
        parts = rule.split("-")
        if parts[0] == parts[2] and parts[0] in sort_phys:
            xisx.append(parts[0])

    # Transform sprites (x-is-y == x becomes y)
    for rule in rules:
        parts = rule.split("-")
        if parts[0] not in xisx and is_obj_word(parts[0]) and is_obj_word(parts[2]):
            all_objs = sort_phys[parts[0]].copy()
            for obj in all_objs:
                change_sprite(obj, parts[2], om, bm, phys, sort_phys)


# Changes a sprite from one thing to another
def change_sprite(o, w, om, bm, phys, sort_phys):
    character = name_to_character[w + "_obj"]
    o2 = GameObj.create_physical_object(w, imgHash[character], o.x, o.y)
    phys.append(o2)  # in with the new...

    # Replace object on obj_map/back_map
    if obj_at_pos(o.y, o.x, om) == o:
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
            # Get all of the sprites for each group
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