from abc import ABC, abstractmethod
from typing import List
from Keke_PY.baba import GameState


class AIInterface(ABC):
    """
    Common AI interface for all search algorithms.
    """

    @abstractmethod
    def search(self, initial_state: GameState, max_forward_model_calls: int = 50) -> List[str]:
        """
        Method to perform search.
        :param initial_state: The initial state of the game.
        :param max_forward_model_calls: Maximum depth for algorithms like DFS.
        :return: List of actions that lead to a solution (if found).
        """
        pass