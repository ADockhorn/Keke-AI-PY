from Keke_PY.heuristics.ParametrisedHeuristic import Heuristic
from Keke_PY.keke_game.baba import GameState


class ZeroHeuristic(Heuristic):
    def run(self, state: GameState, ctx: dict, *args: float) -> float:
        return 0
