from Keke_PY.heuristics.ParametrisedHeuristic import Heuristic
from Keke_PY.keke_game.baba import GameState


class SimpleHeuristic(Heuristic):

    def run(self, state: GameState, ctx: dict, *args: float) -> float:
        """
        A simple heuristic function that estimates the cost to the goal.
        In this case, it calculates the Manhattan distance between the player and the winning object.

        :param state: The current game state.
        :param ctx: Context given to the heuristics
        :return: Estimated cost to reach the goal.
        """
        if len(state.players) == 0:
            return 10 * float(len(state.object_map) + len(state.object_map[0]))
        if not state.winnables:
            return float('inf')  # No winnable objects

        # Calculate Manhattan distance from each player to the closest winnable object
        return min([min(abs(player.x - winnable.x) + abs(player.y - winnable.y) for winnable in state.winnables) for player in state.players])
