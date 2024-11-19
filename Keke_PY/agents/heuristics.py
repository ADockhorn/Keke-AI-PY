import math
from typing import List, Callable, Union

from Keke_PY.baba import GameState, parse_map, double_map_to_string, GameObj, Direction, GameObjectType

important_SuffixWords = ["win", "push", "you"]
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
    return -math.log(len(state.winnables), math.e)

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

    def isInRule(word: GameObj) -> bool:
        for used_word in state.rule_objs:
            if used_word.x == word.x and used_word.y == word.y:
                return True
        return False

    counter: int = 0
    for word in checking_these_words:
        if not isInRule(word) and suffixIsStuck(state, word.x, word.y):
            counter += 1
    for word in state.is_connectors:
        if not isInRule(word) and isIsStuck(state, word.x, word.y):
            counter += 1
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
    # TODO: Suggestion: Instead of counting an 'IS' as usable, if it is connected to a *-fix,
    #       we could count the direction of the *-fix as unblocked
    # TODO: Suggestion: Is there a reason, we itterate throu all words for this?
    #       Can't we just check the corresponding positions?
    for word in state.words:
        if word.name in allPrefixes:
            if word.x == x - 1 and word.y == y:
                return False
            if word.x == x and word.y == y - 1:
                return False
        if word.name in allSuffixes:
            if word.x == x + 1 and word.y == y:
                return False
            if word.x == x and word.y == y + 1:
                return False

    
    blockedDirs = [
        isDirectionBlocked(state, x, y, Direction.Left),
        isDirectionBlocked(state, x, y, Direction.Up),
        isDirectionBlocked(state, x, y, Direction.Right),
        isDirectionBlocked(state, x, y, Direction.Down),
    ]

    for i in range(4):
        if blockedDirs[i] and blockedDirs[(i + 1) % 4]:
            return True
    return False




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
    # TODO: Suggestion: Is there a reason, we itterate throu all words for this?
    #       Can't we just check the corresponding positions?
    for is_connector in state.is_connectors:
        # TODO: first condition in original code (ll. 236) should never be true
        #   (I omitted it, since I think it's an accidental copy)
        if is_connector.x == x - 1 and is_connector.y == y:
            # TODO: Suggestion: Couldn't we return, whether the 'IS' is stuck?
            return False
        if is_connector.x == x and is_connector.y == y - 1:
            # TODO: Suggestion: Couldn't we return, whether the 'IS' is stuck?
            return False
    # If a suffix is stuck in the upper left corner, it can't be connected into a rule
    return (
        isDirectionBlocked(state, x, y, Direction.Left) and
        isDirectionBlocked(state, x, y, Direction.Up)
    )

def isDirectionBlocked(state: GameState, x: int, y: int, direction: Direction) -> bool:
    # TODO: document this function
    dx, dy = {
        Direction.Up: [0, -1],
        Direction.Left: [-1, 0],
        Direction.Down: [0, 1],
        Direction.Right: [1, 0],
    }[direction]

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
        if obj_map_obj.is_stopped:
            return True
        # TODO: Does '.type === "word"'(js) include '.object_type == Keyword'?????
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
        if obj.is_stoped:
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
    #TODO: Code and documentation do not match!?!?!?!
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
    # TODO: clarify functionality of js code (shouldn't line 826 be about temp2, if not, shouldn't the function always return []?)

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

    #TODO: distanceHeuristic
    maximizeDifferentRules,

    #TODO: minimizeDistanceToIsIfOnlyOneWinExists
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













