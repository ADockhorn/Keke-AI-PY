from collections import deque

from Keke_PY.search_agents.ai_interface import AIInterface, range_or_infinite_loop
from Keke_PY.keke_game.keke import GameState, Direction, check_win, advance_game_state
from typing import List, Tuple, Union


class BFS(AIInterface):
    """
    Breadth-First Search implementation.
    """

    def search(
            self,
            initial_state: GameState,
            max_forward_model_calls: Union[int, None] = None,
            max_depth: Union[int, None] = None,
            print_progress_bar: bool = False
    ) -> Tuple[Union[List[str], None], int]:
        """
        :param initial_state: The initial state of the game.
        :param max_forward_model_calls: Maximum number of node expansions to avoid infinite loops.
        :param max_depth: Maximum depth for algorithms like DFS.
        :param print_progress_bar: if True, there will be a progress-bar in the console for the solving-attempt.
        :return: List of actions that lead to a solution (if found, else None), and the number of node expansions.
        """
        queue = deque([(initial_state, [])])  # (current state, action history)
        visited = set()

        for i in range_or_infinite_loop(max_forward_model_calls, print_progress_bar):
            if not queue:
                break
            current_state, actions = queue.popleft()

            # Check if we have won the game
            if check_win(current_state):
                return actions, i

            # Mark this state as visited
            state_str = current_state.unique_str()  # Serialize the state to check for duplicates
            if state_str in visited:
                continue
            visited.add(state_str)

            # Get all possible actions and apply them
            if max_depth is None or len(actions) < max_depth:
                for action in [Direction.Up, Direction.Down, Direction.Left, Direction.Right, Direction.Wait]:
                    next_state = advance_game_state(action, current_state.copy())
                    if next_state.unique_str() not in visited:
                        queue.append((next_state, actions + [action.name]))

        return None, max_forward_model_calls  # Return empty if no solution is found


if __name__ == '__main__':
    from Keke_PY.keke_game.simulation import load_level_set, parse_map, map_to_string, make_level
    level_set = load_level_set("json_levels/demo_LEVELS.json")

    demo_levels = level_set["levels"]
    for level in demo_levels:
        game_map = parse_map(level["ascii"])
        print(map_to_string(game_map))

        game_state = make_level(game_map)

        agent = BFS()
        solution = agent.search(game_state, max_forward_model_calls=100000)
        print(solution)
