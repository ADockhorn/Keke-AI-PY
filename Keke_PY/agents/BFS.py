from collections import deque
from ai_interface import AIInterface
from Keke_PY.baba import GameState, Direction, check_win, advance_game_state
from typing import List, Tuple, Union
from tqdm import trange


class BFS(AIInterface):
    """
    Breadth-First Search implementation.
    """

    def search(self, initial_state: GameState, max_forward_model_calls: int = 50) -> Tuple[Union[List[str], None], int]:
        queue = deque([(initial_state, [])])  # (current state, action history)
        visited = set()

        for i in trange(max_forward_model_calls):
            if not queue:
                break
            current_state, actions = queue.popleft()

            # Check if we have won the game
            if check_win(current_state):
                return actions, i

            # Mark this state as visited
            state_str = str(current_state)  # Serialize the state to check for duplicates
            if state_str in visited:
                continue
            visited.add(state_str)

            # Get all possible actions and apply them
            for action in [Direction.Up, Direction.Down, Direction.Left, Direction.Right, Direction.Wait]:
                next_state = advance_game_state(action, current_state.copy())
                if str(next_state) not in visited:
                    queue.append((next_state, actions + [action.name]))

        return None, max_forward_model_calls  # Return empty if no solution is found


if __name__ == '__main__':
    from Keke_PY.simulation import load_level_set, parse_map, map_to_string, make_level
    level_set = load_level_set("json_levels/demo_LEVELS.json")

    demo_levels = level_set["levels"]
    for level in demo_levels:
        game_map = parse_map(level["ascii"])
        print(map_to_string(game_map))

        game_state = make_level(game_map)

        agent = BFS()
        solution = agent.search(game_state, max_forward_model_calls=100000)
        print(solution)
