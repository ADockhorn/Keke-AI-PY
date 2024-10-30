from collections import deque
from ai_interface import AIInterface
from Keke_PY.baba import GameState, check_win, Direction
from Keke_PY.simulation import advance_game_state
from typing import List


class DFS(AIInterface):
    """
    Depth-First Search implementation.
    """

    def search(self, initial_state: GameState, max_depth: int = 50) -> List[str]:
        stack = [(initial_state, [])]  # (current state, action history)
        visited = set()

        while stack:
            current_state, actions = stack.pop()

            # Check if we have won the game
            if check_win(current_state.players, current_state.winnables):
                return actions

            # Mark this state as visited
            state_str = str(current_state)  # Serialize the state to check for duplicates
            if state_str in visited:
                continue
            visited.add(state_str)

            # Get all possible actions and apply them
            if len(actions) < max_depth:
                for action in [Direction.Up, Direction.Down, Direction.Left, Direction.Right, Direction.Wait]:
                    next_state = advance_game_state(action, current_state.copy())["next_state"]
                    if str(next_state) not in visited:
                        stack.append((next_state, actions + [action.name]))

        return []  # Return empty if no solution is found
