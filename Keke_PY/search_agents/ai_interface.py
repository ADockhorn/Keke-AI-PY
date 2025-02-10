from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import List, Tuple, Union, Iterable

from tqdm import trange

from Keke_PY.keke_game.baba import GameState


class AIInterface(ABC):
    """
    Common AI interface for all search algorithms.
    """

    @abstractmethod
    def search(
            self,
            initial_state: GameState,
            max_forward_model_calls: Union[int, None] = None,
            max_depth: Union[int, None] = None,
            print_progress_bar: bool = False
    ) -> Tuple[Union[List[str], None], int]:
        """
        Method to perform search.
        :param initial_state: The initial state of the game.
        :param max_forward_model_calls: Maximum number of node expansions to avoid infinite loops.
        :param max_depth: Maximum depth for algorithms like DFS.
        :param print_progress_bar: if True, there will be a progress-bar in the console for the solving-attempt.
        :return: List of actions that lead to a solution (if found, else None), and the number of node expansions.
        """
        pass


def range_or_infinite_loop(end: Union[int, None], print_progress_bar: bool) -> Iterable:

    range_constructor: Callable[[int], Iterable] = trange if print_progress_bar else range

    if end.__class__ == int:
        try:
            for i in range_constructor(end):
                yield i
            return
        except OverflowError:
            pass

    count: int = 0
    while True:
        for _ in range_constructor(1000000):
            yield count
            count += 1