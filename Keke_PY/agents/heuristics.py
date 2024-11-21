import math
from typing import List, Callable, Union

from Keke_PY.baba import GameState, parse_map, double_map_to_string, GameObj, Direction, GameObjectType

important_SuffixWords = ["win", "push", "you"]

# BIG TODO: change Objects to Enums or alike
allPrefixes = ["lava", "skull", "love", "goop", "flag", "rock", "wall", "floor", "grass", "baba", "keke"]
allSuffixes = ["stop", "sink", "push", "you", "kill", "hot", "move", "melt", "you", "win"]


"""/**
 * Returns negative number of goals on current map multiplied by a weight.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the negative number of goals.
 */"""
def nbrOfGoals(state: GameState) -> float:
    # TODO@ask: description doesn't include the logarithm:
    if len(state.winnables) != 0:
        return -math.log(len(state.winnables), math.e)
    else:
        return math.inf # TODO@ask!: is this intended behavior? (the js code works like this)

"""/**
 * Returns negative number of players on current map multiplied by a weight.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the negative number of players.
 */"""
def nbrOfPlayers(state: GameState) -> float:
    return -len(state.players)

"""/**
 * Returns the amount of closed rooms multiplied by a weight.
 * Close Room = A closed space from which you cannot move to another room.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the amount of closed rooms.
 */"""
def connectivity(state: GameState) -> float:
    map: List[List[str]] = parseRoomForConnectivityFeature(state)
    roomCount: int = 0
    for i, row in enumerate(map):
        for j, char in enumerate(row):
            if char == '0':
                roomCount += 1
                mark_all_connected(map, i, j, len(map), len(row))
    return roomCount

"""/**
 * Returns the amount of IS-words and important Suffixes (look at variable at the beginning of this file)
 * that cannot be used to form a rule anymore, multiplied by a weight.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The IS and important suffixes that are "out of play", multiplied hy a weight.
 */"""
def outOfPlan(state: GameState) -> float:

    checking_these_words: List[GameObj] = []
    for word in state.words:
        if word.name in important_SuffixWords:
            checking_these_words.append(word)

    counter: int = 0
    for word in checking_these_words:
        # checking, if the suffix is in a rule is not needed, since suffixIsStuck() does that implicitly
        if suffixIsStuck(state, word.x, word.y):
            counter += 1
    for word in state.is_connectors:
        # checking, if the 'IS' is in a rule is not needed, since isIsStuck() does that implicitly
        if isIsStuck(state, word.x, word.y):
            counter += 1
    # TODO@ask: wouldn't is be nice to also check for stuck pre-fixes? Or are they less valuable?
    return counter



"""/**
 * Checks if an IS-word is stuck, while not being connected to a word.
 *
 * @param {object} state The current gamestate.
 * @param {number} x the x-Position of the IS-word.
 * @param {number} y the y-Position of the IS-word.
 * @return {boolean} Whether the IS-word is stuck and useless.
 */"""
def isIsStuck(state: GameState, x: int, y: int) -> bool:
    # An 'IS' is counted as not stuck, if it is free in one axis (= not stuck in a corner)
    # If one direction is blocked by a word, that could create a rule with the 'IS',
    #       the direction is counted as free, since the 'IS' can still be used,
    #       if the opposite direction is free.
    # TODO@ask: above definition would have considered the following as free:
    #       _____   w: prefix
    #       _wib    i: 'IS'
    #       _____   b: boulder
    #    New Suggestion (the code below):
    #       checks whether the 'IS' can be directly moved or directly completable (independently)
    #       direct moving means without shifting any blocking object sideways out of the way
    #       direct completing means by only adding rule parts
    #       (checking indirect movability/completibility would be to resource intensive)
    #           (compared to the js implementation, this only additionally checks,
    #               whether the incomplete side of a rule is free)
    def is_free_or_usable(direction: Direction, usable_names: List[str]) -> bool:
        dx, dy = direction.dx(), direction.dy()
        if is_field_empty(state, x + dx, y + dy):
            return True
        connected_field = state.back_map[y + dy][x + dx]
        return connected_field is GameObj and connected_field.name in usable_names

    if (
        is_free_or_usable(Direction.Up, allPrefixes) and
        is_free_or_usable(Direction.Down, allSuffixes)
    ):
        return False
    if (
        is_free_or_usable(Direction.Left, allPrefixes) and
        is_free_or_usable(Direction.Right, allSuffixes)
    ):
        return False

    return not is_movable_in_any_axis(state, x, y)



"""/**
 * Checks if an important Suffix (Defined list at the beginning of this File) is stuck, 
 * while not being connected to an IS-word.
 *
 * @param {object} state The current gamestate.
 * @param {number} x the x-Position of the Suffix.
 * @param {number} y the y-Position of the Suffix.
 * @return {boolean} Whether the Suffix is stuck and useless.
 */"""
def suffixIsStuck(state: GameState, x: int, y: int) -> bool:
    # Check, if a suffix might be usable by a connected 'IS':
    # TODO: Is there a reason, we itterate throu all words for this?
    #       Can't we just check the corresponding positions?
    for is_connector in state.is_connectors:
        if is_connector.x == x - 1 and is_connector.y == y:
            # TODO: Couldn't we return, whether the 'IS' is stuck?
            return False
        if is_connector.x == x and is_connector.y == y - 1:
            # TODO: Couldn't we return, whether the 'IS' is stuck?
            return False
    # If a suffix is stuck in the upper left corner, it can't be connected into a rule
    return (
            is_direction_blocked(state, x, y, Direction.Left) and
            is_direction_blocked(state, x, y, Direction.Up)
    )

def is_field_empty(state: GameState, x: int, y: int) -> bool:
    return (
        state.back_map[y][x] == ' ' and
        state.obj_map[y][x] == ' '
    )

def is_movable_in_any_axis(state: GameState, x: int, y: int) -> bool:
    # TODO: document this function
    return not (
        is_direction_blocked(state, x, y, Direction.Up) or
        is_direction_blocked(state, x, y, Direction.Down)
    ) or not (
        is_direction_blocked(state, x, y, Direction.Left) or
        is_direction_blocked(state, x, y, Direction.Right)
    )

def is_direction_blocked(state: GameState, x: int, y: int, direction: Direction) -> bool:
    # TODO: document this function
    dx, dy = direction.dx(), direction.dy()

    while True:
        x += dx
        y += dy
        back_map_obj: Union[GameObj, str] = state.back_map[y][x]
        if back_map_obj == '_':
            return True
        if back_map_obj == ' ':
            # TODO: What if there is a stoped object in the obj_map?!?!
            #       Shouldn't we check that first?!?!
            return False
        obj_map_obj: Union[GameObj, str] = state.obj_map[y][x]
        if obj_map_obj is not GameObj:
            if obj_map_obj == ' ':
                return False
            else:
                return True # TODO: Could this be something else?
        if obj_map_obj.is_stopped:
            return True
        # TODO: Does '.type === "word"'(js) include '.object_type == Keyword'????? - Yes
        if obj_map_obj.object_type not in [GameObjectType.Word, GameObjectType.Keyword]:
            return False


"""/**
 * Returns number of auto_movers on current map multiplied by a weight.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the number of automovers.
 */"""
def elimOfAutomovers(state: GameState) -> float:
    return len(state.auto_movers)

"""/**
 * Returns number of killer objects on current map multiplied by a weight.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the number of killers.
 */"""
def elimOfThreads(state: GameState) -> float:
    return len(state.killers)

"""/**
 * Returns negative number of pushable objects on current map multiplied by a weight.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the negative number of pushables.
 */"""
def maximizePushables(state: GameState) -> float:
    return len(state.pushables)


"""/**
 * Returns number of sinkers on current map multiplied by a weight.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the number of sinkers.
 */"""
def minimizeSinkables(state: GameState) -> float:
    return len(state.sinkers)


"""/**
 * Returns number of stopping objects on current map multiplied by a weight.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the number of stopping objects.
 */"""
def minimizeStopables(state: GameState) -> float:
    count: int = 0
    for obj in state.phys:
        if obj.is_stopped:
            count += 1
    return count



"""/**
 * Calculates average distance from player objects to killing objects and multiplies it with a weight.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the average distance to killing objects.
 */"""
def distanceToKillables(state: GameState) -> float:
    return avgDistance(state.players, state.killers) or 0.0


"""/**
 * Tracks the amount of unique rules that where created during a level.
 *
 * @param {object} state The current gamestate.
 * @param {number} weight The weight of this heuristic being multiplied.
 * @return {number} The weight multiplied with the amount of unique rules.
 */"""
def maximizeDifferentRules(state: GameState) -> float:
    #TODO: shal this function actualy use a global variable?
    #       I assumed, 'allrules' should be empty every time, in the following code
    # TODO: Is this code the intended behavior?
    #       - No: compare to parent node!!!
    return len(set(state.rules))




"""/**
 * Calculates the average Distance between two groups of objects.
 *
 * @param {object[]} g1 First group of objects.
 * @param {object[]} g2 Second group of objects.
 * @return {number} Average distance between the given groups of objects.
 */"""
def avgDistance(group1: List[GameObj], group2: List[GameObj]) -> Union[float, None]:
    distance_sum: float = 0
    distances_count: int = 0
    for obj1 in group1:
        for obj2 in group2:
            distances_count += 1
            distance_sum += dist(obj1, obj2)
    if distances_count == 0:
        return None
    return distance_sum / distances_count








"""/**
 * Eukleadean Distance of Object1 to Object2
 *
 * @param {object} a The first object.
 * @param {object} b The second object.
 * @return {number} The distance from Object a to Object b.
 */"""
def dist(a: GameObj, b: GameObj) -> float:
    #TODO: Change documentation to manhatan dist
    return abs(a.x - b.x) + abs(a.y - b.y)



"""/**
 * Parses a map in a way, that other functions like the _connectivity function can read it.
 * All walls and objects, where the player can (or shouldn't because death) not move on, are a "1".
 * All empty fields, fields with only overlappable objects, and playerfields are a "0".
 *
 * @param {object} state The current gamestate.
 * @return {string[]} The parsed map.
 */"""
def parseRoomForConnectivityFeature(state: GameState) -> List[List[str]]:
    map = parse_map(double_map_to_string(state.obj_map, state.back_map))

    for i, row in enumerate(map):
        for j, char in enumerate(row):
            if char == '_':
                map[i][j] = '1'
            else:
                map[i][j] = '0'

    def set_all(objs: List[GameObj], c: str):
        for obj in objs:
            map[obj.y][obj.x] = c

    set_all(state.killers, '1')
    set_all(state.pushables, '1')
    set_all(state.sinkers, '1')
    set_all(findHotMelt(state), '1')
    set_all(state.phys, '1')
    set_all(state.players, '0')
    set_all(state.winnables, '0')

    return map



"""/**
 * Returns all objects, that are hot IF the player is melt. Otherwise just and empty list.
 *
 * @param {object} state The current gamestate.
 * @return {object[]} All objects, that are currently hot.
 */"""
def findHotMelt(state: GameState) -> List[GameObj]:

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
 * Recursive function that takes a parsed map and marks visited positions with a "1".
 * If neighboring positions where not visited yet, the function calls itself with said neighboring position.
 *
 * @param {string[]} map The map of the level parsed to 0s and 1s. (0=empty and not visited field 1=wall or visited field)
 * @param {number} i The current y position on the map.
 * @param {number} j The current x position on the map.
 * @param {number} mapL The maximum i dimension.
 * @param {number} rowL The maximum j dimension.
 */"""
def mark_all_connected(map: List[List[str]], x: int, y: int, size_x: int, size_y: int):
    if x < 0 or x >= size_x or y < 0 or y >= size_y:
        return
    if map[x][y] == '1':
        return
    map[x][y] = '1'
    mark_all_connected(map, x - 1, y, size_x, size_y)
    mark_all_connected(map, x + 1, y, size_x, size_y)
    mark_all_connected(map, x, y - 1, size_x, size_y)
    mark_all_connected(map, x, y + 1, size_x, size_y)


# TODO: the naming 'maximize'/'minimize' is inconsistent with the -/+ factor!!!
#       -> rename: don't assume min-/maximization

heuristics: List[Callable[[GameState], float]] = [

    nbrOfGoals,
    nbrOfPlayers,
    connectivity,
    outOfPlan,
    elimOfAutomovers,

    elimOfThreads,
    maximizePushables,
    minimizeSinkables,
    minimizeStopables,
    distanceToKillables,

    #TODO: distanceHeuristic TODO: split into multiple
    maximizeDifferentRules,

    #TODO: minimizeDistanceToIsIfOnlyOneWinExists (wird evtl. später weggelassen)
    #TODO: goalPath

]



def weightedHeuristicSum(
    state: GameState,
    weights: List[float],
    doNothingThreshold: float = 0.01
) -> float:
    feature_sum: float = 0.0
    for heuristic, weight in zip(heuristics, weights):
        if abs(weight) > doNothingThreshold:
            feature_sum += weight * heuristic(state)
    return feature_sum













