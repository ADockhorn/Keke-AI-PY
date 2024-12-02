from abc import ABC, abstractmethod
from decimal import Overflow
from typing import List, Tuple, Union, Iterable

from tqdm import trange

from Keke_PY.baba import GameState


class AIInterface(ABC):
    """
    Common AI interface for all search algorithms.
    """

    @abstractmethod
    def search(self, initial_state: GameState, max_forward_model_calls: Union[int, None] = 50, max_depth: Union[int, None] = 50) -> Tuple[Union[List[str], None], int]:
        """
        Method to perform search.
        :param initial_state: The initial state of the game.
        :param max_forward_model_calls: Maximum number of node expansions to avoid infinite loops.
        :param max_depth: Maximum depth for algorithms like DFS.
        :return: List of actions that lead to a solution (if found, else None), and the number of node expansions.
        """
        pass


def trange_or_infinite_loop(end: Union[int, None]) -> Iterable:

    if end.__class__ == int:
        try:
            for i in trange(end):
                yield i
            return
        except OverflowError:
            pass

    while True:
        for i in trange(1000000):
            yield i