from collections import deque
from tqdm import trange
from ai_interface import AIInterface
from Keke_PY.baba import GameState, check_win, Direction
from Keke_PY.simulation import advance_game_state
from typing import List, Tuple, Union


class DFS(AIInterface):
    """
    Depth-First Search implementation.
    """

    def search(self, initial_state: GameState, max_forward_model_calls: int = 50, max_depth: int = 50) -> Tuple[Union[List[str], None], int]:
        """
        :param initial_state: The initial state of the game.
        :param max_forward_model_calls: Maximum number of node expansions to avoid infinite loops.
        :param max_depth: Maximum depth for algorithms like DFS.
        :return: List of actions that lead to a solution (if found, else None), and the number of node expansions.
        """
        stack = [(initial_state, [])]  # (current state, action history)
        visited = set()

        for i in trange(max_forward_model_calls):
            if not stack:
                break
            current_state, actions = stack.pop()

            # Check if we have won the game
            if check_win(current_state):
                return actions, i

            # Mark this state as visited
            state_str = str(current_state)  # Serialize the state to check for duplicates
            if state_str in visited:
                continue
            visited.add(state_str)

            # Get all possible actions and apply them
            if len(actions) < max_depth:
                for action in [Direction.Up, Direction.Down, Direction.Left, Direction.Right, Direction.Wait]:
                    next_state = advance_game_state(action, current_state.copy())
                    if str(next_state) not in visited:
                        stack.append((next_state, actions + [action.name]))

        return [], max_forward_model_calls  # Return empty if no solution is found
