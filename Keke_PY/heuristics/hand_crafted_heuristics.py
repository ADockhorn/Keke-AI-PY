from typing import List, Callable, Union, Optional

from Keke_PY.baba import GameState, parse_map, only_top_objects_string, GameObj, Direction, GameObjectType
from Keke_PY.heuristics.ParametrisedHeuristic import ParametrisedHeuristic

important_SuffixWords = ["win", "push", "you"]

# BIG TODO: change Objects to Enums or alike
allPrefixes = ["lava", "skull", "love", "goop", "flag", "rock", "wall", "floor", "grass", "baba", "keke"]
allSuffixes = ["stop", "sink", "push", "you", "kill", "hot", "move", "melt", "you", "win"]


"""/**
 * Returns negative number of goals on current blocked_fields_map multiplied by a weight.
 *
 * @param {object} state The current game-state.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the negative number of goals.
 */"""
def number_of_goal_objects(state: GameState, _ctx: dict) -> float:
    return len(state.winnables)

"""/**
 * Returns negative number of players on current blocked_fields_map multiplied by a weight.
 *
 * @param {object} state The current game-state.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the negative number of players.
 */"""
def number_of_player_objects(state: GameState, _ctx: dict) -> float:
    return -len(state.players)

"""/**
 * Returns the amount of closed rooms multiplied by a weight.
 * Close Room = A closed space from which you cannot move to another room.
 *
 * @param {object} state The current game-state.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the amount of closed rooms.
 */"""
def connectivity(state: GameState, _ctx: dict) -> float:
    char_map: List[List[str]] = parse_room_for_connectivity_feature(state)
    room_count: int = 0
    for i, row in enumerate(char_map):
        for j, char in enumerate(row):
            if char == '0':
                room_count += 1
                mark_all_connected(char_map, i, j, len(char_map), len(row))
    return room_count


def number_of_stuck_is_words(state: GameState, _ctx: dict) -> float:
    """
    Number of stuck 'IS'-words.
    (For a clarification of what 'stuck' means, see 'isIsStuck()')
    @param state is the current game-state
    @param _ctx is the (unused) context given to the heuristics
    @return number of stuck 'IS'-words
    """
    counter: int = 0
    for word in state.is_connectors:
        if is_is_word_stuck(state, word.x, word.y):
            counter += 1
    return counter

def number_of_stuck_prefixes(state: GameState, _ctx: dict) -> float:
    """
    Number of stuck prefixes.
    (For a clarification of what 'stuck' means, see 'prefixIsStuck()')
    @param state is the current game-state
    @param _ctx is the (unused) context given to the heuristics
    @return number of stuck prefixes
    """
    counter: int = 0
    for word in state.words:
        if word.name in allPrefixes and is_prefix_stuck(state, word.x, word.y):
                counter += 1
    return counter

def number_of_stuck_suffixes(state: GameState, _ctx: dict) -> float:
    """
    Number of stuck suffixes.
    (For a clarification of what 'stuck' means, see 'suffixIsStuck()')
    @param state is the current game-state
    @param _ctx is the (unused) context given to the heuristics
    @return number of stuck suffixes
    """
    counter: int = 0
    for word in state.words:
        if word.name in allSuffixes and is_suffix_stuck(state, word.x, word.y):
                counter += 1
    return counter

def number_of_stuck_important_suffixes(state: GameState, _ctx: dict) -> float:
    """
    Number of stuck important suffixes. (As defined above by 'important_SuffixWords')
    (For a clarification of what 'stuck' means, see 'suffixIsStuck()')
    @param state is the current game-state
    @param _ctx is the (unused) context given to the heuristics
    @return number of stuck important suffixes
    """
    counter: int = 0
    for word in state.words:
        if word.name in important_SuffixWords and is_suffix_stuck(state, word.x, word.y):
                counter += 1
    return counter



def is_is_word_stuck(state: GameState, x: int, y: int) -> bool:
    """
    Checks whether an 'IS' can't be instantly moved or instantly completed (independently).
        Instant moving means by one push / without shifting any blocking object sideways out of the way.
        Instant completing means by only adding rule parts on empty fields.
        (checking not instant movability/completability would be to resource intensive)
        (compared to the js implementation, this only additionally checks,
            whether the incomplete side of a rule is free)
    (This does not check the 'IS''s field itself.)
    @param state is the current game-state
    @param x is the x-coordinate of the 'IS'
    @param y is the y-coordinate of the 'IS'
    @return whether the 'IS' is stuck
    """

    if (
        is_free_or_usable(state, x, y - 1, allPrefixes) and
        is_free_or_usable(state, x, y + 1, allSuffixes)
    ):
        return False
    if (
        is_free_or_usable(state, x - 1, y, allPrefixes) and
        is_free_or_usable(state, x + 1, y, allSuffixes)
    ):
        return False

    return not is_movable_in_any_axis(state, x, y)



def is_suffix_stuck(state: GameState, x: int, y: int) -> bool:
    """
    Checks whether a Suffix can't be instantly moved or instantly completed (independently).
        Instant moving means by one push / without shifting any blocking object sideways out of the way.
        Instant completing means by only adding rule parts on empty fields.
        (checking not instant movability/completability would be to resource intensive)
        (compared to the js implementation, this should cover more cases of stuckness:
            . . x .       . can be anything; _ is stopped in some way;
            . . . .       x is anything but a prefix; the y is anything but 'IS';
            . y s _       the suffix s is now considered stuck, since it can't be instantly moved or completed;
            . . b .       the boulder b (or x) might be moved to free s, but this (and the previous) implementation
            . . _ .            do not consider these (not instant) movements / completions;
        )
    (This does not check the suffix field itself.)
    @param state is the current game-state
    @param x is the x-coordinate of the suffix
    @param y is the y-coordinate of the suffix
    @return whether the suffix is stuck
    """

    if (
        is_free_or_usable(state, x - 2, y, allPrefixes) and
        is_free_or_usable(state, x - 1, y, ['is'])
    ):
        return False
    if (
        is_free_or_usable(state, x, y - 2, allPrefixes) and
        is_free_or_usable(state, x, y - 1, ['is'])
    ):
        return False

    return not is_movable_in_any_axis(state, x, y)

def is_prefix_stuck(state: GameState, x: int, y: int) -> bool:
    """
    Checks whether a Prefix can't be instantly moved or instantly completed (independently).
        Instant moving means by one push / without shifting any blocking object sideways out of the way.
        Instant completing means by only adding rule parts on empty fields.
        (checking not instant movability/completability would be to resource intensive)
        (compared to the js implementation (for suffixes, since there was none for prefixes),
            this should cover more cases of stuckness:
            . _ . .       . can be anything; _ is stopped in some way;
            . b . .       x is anything but a suffix; the y is anything but 'IS';
            _ s y .       the prefix s is now considered stuck, since it can't be instantly moved or completed;
            . . . .       the boulder b (or x) might be moved to free s, but this implementation
            . x . .            do not consider these (not instant) movements / completions;
        )
    (This does not check the prefix field itself.)
    @param state is the current game-state
    @param x is the x-coordinate of the prefix
    @param y is the y-coordinate of the prefix
    @return whether the prefix is stuck
    """

    if (
        is_free_or_usable(state, x + 2, y, allSuffixes) and
        is_free_or_usable(state, x + 1, y, ['is'])
    ):
        return False
    if (
        is_free_or_usable(state, x, y + 2, allSuffixes) and
        is_free_or_usable(state, x, y + 1, ['is'])
    ):
        return False

    return not is_movable_in_any_axis(state, x, y)

def is_free_or_usable(state: GameState, x: int, y: int, usable_names: List[str]) -> bool:
    """
    check for fields, that could in theory complete another field to a rule.
    returns true, if the field doesn't prevent the rule from being completed.
    (The bounds of the blocked_fields_map are not considered free or usable, since nothing can move or be put there)
    @param state is the current game-state
    @param x is x-coordinate of the field to be checked
    @param y is y-coordinate of the field to be checked
    @param usable_names is a list of words that are allowed to be at (x,y) for the rule to work
    @return whether the objects at (x,y) do not prevent the rule from being completed
    """
    if not 0 <= y < len(state.object_map) or not 0 <= x < len(state.object_map[0]):
        return False
    if is_field_empty(state, x, y):
        return True
    connected_field = state.object_map[y][x]
    return any(
        obj.__class__ == GameObj and
        obj.object_type in [GameObjectType.Word, GameObjectType.Keyword] and
        obj.name in usable_names
        for obj in connected_field
    )

def is_field_empty(state: GameState, x: int, y: int) -> bool:
    """
    Checks, whether there is nothing at (x,y)
    (The bounds of the blocked_fields_map are considered as not empty, since nothing can move or be put there)
    @param state is the current game-state
    @param x is x-coordinate of the field to be checked
    @param y is y-coordinate of the field to be checked
    @return whether the field is empty
    """
    return (
        0 <= y < len(state.object_map) and
        0 <= x < len(state.object_map[0]) and
        state.object_map[y][x]
    )

def is_movable_in_any_axis(state: GameState, x: int, y: int) -> bool:
    """
    Checks, whether a position can be pushed.
    To be practically pushable, either both vertical or both horizontal directions have to be free.
    The Idea is, that the player has to push from one side, and the other side has to have space,
    in order to not resist the push.
    (This does not check the field itself.)
    @param state is the current game-state
    @param x is x-coordinate of the field to be checked
    @param y is y-coordinate of the field to be checked
    @return whether the position can be pushed
    """
    return not (
        is_direction_blocked(state, x, y, Direction.Up) or
        is_direction_blocked(state, x, y, Direction.Down)
    ) or not (
        is_direction_blocked(state, x, y, Direction.Left) or
        is_direction_blocked(state, x, y, Direction.Right)
    )

def is_direction_blocked(state: GameState, x: int, y: int, direction: Direction) -> bool:
    """
    Checks, whether a position is blocked in a certain direction.
    A direction is blocked, if - in that direction - there is an unmovable block before any free space
    (This does not check the field itself.)
    @param state is the current game-state
    @param x is x-coordinate of the field to be checked
    @param y is y-coordinate of the field to be checked
    @param direction is the direction in which to check
    @return whether the direction is blocked
    """
    dx, dy = direction.dx(), direction.dy()

    def is_blocking(game_object: Union[GameObj, str]) -> Optional[bool]:
        if game_object.__class__ == GameObj:
            if game_object.is_stopped:
                return True
            if game_object.is_movable:
                return None
            return False
        else:
            if game_object == '_':
                return True
            if game_object == ' ':
                return False
            assert False, f"the value '{game_object}' is unknown to this code" # There should be no other string values

    while True:
        x += dx
        y += dy
        search_further: bool = False
        for obj in state.object_map[y][x]:
            test: Optional[bool] = is_blocking(obj)
            if test:
                return True
            if test is None:
                search_further = True
        if not search_further:
            return False



"""/**
 * Returns number of auto_movers on current blocked_fields_map multiplied by a weight.
 *
 * @param {object} state The current game-state.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the number of auto-movers.
 */"""
def number_of_auto_movers(state: GameState, _ctx: dict) -> float:
    return len(state.auto_movers)

"""/**
 * Returns number of killer objects on current blocked_fields_map multiplied by a weight.
 *
 * @param {object} state The current game-state.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the number of killers.
 */"""
def number_of_killer_objects(state: GameState, _ctx: dict) -> float:
    return len(state.killers)

"""/**
 * Returns negative number of pushable objects on current blocked_fields_map multiplied by a weight.
 *
 * @param {object} state The current game-state.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the number of pushable objects.
 */"""
def number_of_pushable_objects(state: GameState, _ctx: dict) -> float:
    return len(state.pushables)


"""/**
 * Returns number of sinkers on current blocked_fields_map multiplied by a weight.
 *
 * @param {object} state The current game-state.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the number of sinkers.
 */"""
def number_of_sinkable_objects(state: GameState, _ctx: dict) -> float:
    return len(state.sinkers)


"""/**
 * Returns number of stopping objects on current blocked_fields_map multiplied by a weight.
 *
 * @param {object} state The current game-state.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the number of stopping objects.
 */"""
def number_of_stopped_objects(state: GameState, _ctx: dict) -> float:
    count: int = 0
    for obj in state.phys:
        if obj.is_stopped:
            count += 1
    return count



"""/**
 * Calculates average distance from player objects to killing objects and multiplies it with a weight.
 *
 * @param {object} state The current game-state.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the average distance to killing objects.
 */"""
def player_killer_distance(state: GameState, _ctx: dict, default_value: float) -> float:
    avg = average_distance(state.players, state.killers)
    if avg is None:
        return default_value
    return avg



# distanceHeuristics:
def distance_to_winnable_objects(state: GameState, _ctx: dict, default_value: float) -> float:
    """
    The average distance between players and objects that are winnable positions.
    If there are no players or winnable positions, the given default value is returned.
    @param state is the current game-state
    @param _ctx is the (unused) context given to the heuristics
    @param default_value is the value returned, if there are no distances
    @return average distance between players and winnable objects or default_value
    """
    avg = average_distance(state.players, state.winnables)
    if avg is None:
        return default_value
    return avg
def distance_to_words(state: GameState, _ctx: dict, default_value: float) -> float:
    """
    The average distance between players and words.
    If there are no players or words, the given default value is returned.
    @param state is the current game-state
    @param _ctx is the (unused) context given to the heuristics
    @param default_value is the value returned, if there are no distances
    @return average distance between players and words or default_value
    """
    avg = average_distance(state.players, state.words)
    if avg is None:
        return default_value
    return avg
def distance_to_pushable_objects(state: GameState, _ctx: dict, default_value: float) -> float:
    """
    The average distance between players and pushable objects.
    If there are no players or pushable objects, the given default value is returned.
    @param state is the current game-state
    @param _ctx is the (unused) context given to the heuristics
    @param default_value is the value returned, if there are no distances
    @return average distance between players and pushable objects or default_value
    """
    avg = average_distance(state.players, state.pushables)
    if avg is None:
        return default_value
    return avg


"""/**
 * Tracks the amount of unique rules that where created during a level.
 *
 * @param {object} state The current game-state.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the amount of unique rules.
 */"""
def number_of_newly_created_rules(state: GameState, ctx: dict) -> float:
    count: int = 0
    for rule in state.rules:
        if rule not in ctx["initial rules"]:
            count += 1
    return count



"""/**
 * Checks if there is a path from any player object to any winning object.
 *
 * @param {object} state The current game-state.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with -1 if there is a path to goal. Otherwise returns 0.
 */"""
def goal_reachability(state: GameState, _ctx: dict) -> float:
    reachable_map: List[List[str]] = parse_room_for_connectivity_feature(state)
    marks, tests = state.winnables, state.players
    if len(state.players) < len(state.winnables):
        marks, tests = state.players, state.winnables
    for mark in marks:
        mark_all_connected(
            reachable_map,
            mark.x, mark.y,
            len(reachable_map), len(reachable_map[0])
        )
    for test in tests:
        if reachable_map[test.y][test.x] == '1':
            return 1.0
    return 0.0



"""/**
 * Calculates the average Distance between two groups of objects.
 *
 * @param {object[]} g1 First group of objects.
 * @param {object[]} g2 Second group of objects.
 * @return {number} Average distance between the given groups of objects.
 */"""
def average_distance(group1: List[GameObj], group2: List[GameObj]) -> Union[float, None]:
    distance_sum: float = 0
    distances_count: int = 0
    for obj1 in group1:
        for obj2 in group2:
            distances_count += 1
            distance_sum += distance(obj1, obj2)
    if distances_count == 0:
        return None
    return distance_sum / distances_count








def distance(a: GameObj, b: GameObj) -> float:
    """
    Manhattan-distance between two objects
    @param a is the first game-object
    @param b is the second game-object
    @return manhattan-distance between a and b
    """
    return abs(a.x - b.x) + abs(a.y - b.y)



"""/**
 * Parses a blocked_fields_map in a way, that other functions like the _connectivity function can read it.
 * All walls and objects, where the player can (or shouldn't because death) not move on, are a "1".
 * All empty fields, fields with only overlapped objects, and player fields are a "0".
 *
 * @param {object} state The current game-state.
 * @return {string[]} The parsed blocked_fields_map.
 */"""
def parse_room_for_connectivity_feature(state: GameState) -> List[List[str]]:
    blocked_fields_map = parse_map(only_top_objects_string(state))

    for i, row in enumerate(blocked_fields_map):
        for j, char in enumerate(row):
            if char == '_':
                blocked_fields_map[i][j] = '1'
            else:
                blocked_fields_map[i][j] = '0'

    def set_all(objs: List[GameObj], c: str):
        for obj in objs:
            blocked_fields_map[obj.y][obj.x] = c

    set_all(state.killers, '1')
    set_all(state.pushables, '1')
    set_all(state.sinkers, '1')
    set_all(hot_objects_if_dangerous(state), '1')
    set_all(state.phys, '1')
    set_all(state.players, '0')
    set_all(state.winnables, '0')

    return blocked_fields_map



"""/**
 * Returns all objects, that are hot IF the player is melt. Otherwise just and empty list.
 *
 * @param {object} state The current game-state.
 * @return {object[]} All objects, that are currently hot.
 */"""
def hot_objects_if_dangerous(state: GameState) -> List[GameObj]:

    hots: List[str] = []
    for rule in state.rules:
        if "is-hot" in rule:
            hots.append(rule)
    if len(hots) <= 0:
        return []

    melts: List[str] = []
    for rule in state.rules:
        if "is-melt" in rule:
            melts.append(rule)
    if len(melts) <= 0:
        return []

    for i in range(len(melts)):
        melts[i] = melts[i].replace("-is-melt", "")

    if not any(map(lambda p: p.name in melts, state.players)):
        return []

    for i in range(len(hots)):
        hots[i] = hots[i].replace("-is-melt", "")

    return list(filter(lambda obj: obj.name in hots, state.phys))




"""/**
 * Helper Function for the connectivity function.
 * Recursive function that takes a parsed blocked_fields_map and marks visited positions with a "1".
 * If neighboring positions where not visited yet, the function calls itself with said neighboring position.
 *
 * @param {string[]} blocked_fields_map The blocked_fields_map of the level parsed to 0s and 1s. (0=empty and not visited field 1=wall or visited field)
 * @param {number} i The current y position on the blocked_fields_map.
 * @param {number} j The current x position on the blocked_fields_map.
 * @param {number} mapL The maximum i dimension.
 * @param {number} rowL The maximum j dimension.
 */"""
def mark_all_connected(blocked_fields_map: List[List[str]], x: int, y: int, size_x: int, size_y: int):
    if x < 0 or x >= size_x or y < 0 or y >= size_y:
        return
    if blocked_fields_map[x][y] == '1':
        return
    blocked_fields_map[x][y] = '1'
    mark_all_connected(blocked_fields_map, x - 1, y, size_x, size_y)
    mark_all_connected(blocked_fields_map, x + 1, y, size_x, size_y)
    mark_all_connected(blocked_fields_map, x, y - 1, size_x, size_y)
    mark_all_connected(blocked_fields_map, x, y + 1, size_x, size_y)



raw_heuristics: List[Callable] = [

    number_of_goal_objects,
    number_of_player_objects,
    connectivity,
    number_of_auto_movers,

    number_of_stuck_is_words,
    number_of_stuck_prefixes,
    number_of_stuck_suffixes,
    number_of_stuck_important_suffixes,

    number_of_killer_objects,
    number_of_pushable_objects,
    number_of_sinkable_objects,
    number_of_stopped_objects,
    player_killer_distance,

    distance_to_winnable_objects,
    distance_to_words,
    distance_to_pushable_objects,

    number_of_newly_created_rules,

    goal_reachability

]

heuristics: List[ParametrisedHeuristic] = [
    ParametrisedHeuristic.from_func(h) for h in raw_heuristics
]

heuristics_feature_vector_length: int = sum(map(
    lambda heuristic: 1 + heuristic.nr_of_parameters,
    heuristics
))
