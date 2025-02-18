import heapq

from Keke_PY.heuristics.ParametrisedHeuristic import Heuristic
from Keke_PY.heuristics.SimpleHeuristic import SimpleHeuristic
from Keke_PY.keke_game.baba import GameState, Direction, check_win, advance_game_state
from Keke_PY.search_agents.ai_interface import AIInterface, range_or_infinite_loop, AgentFromPolicy
from typing import List, Tuple, Union


class AStar(AIInterface):
    """
    A* Search Agent implementation.
    """

    def __init__(self, heuristic: Heuristic):
        """
        Initialize the A* agent with a heuristic function.

        :param heuristic: A function that estimates the cost from the current state to the goal.
        """
        assert heuristic.nr_of_parameters == 0, "heuristic is not allowed to expect any parameters."
        self.heuristic = heuristic

    def search(
            self,
            initial_state: GameState,
            max_forward_model_calls: Union[int, None] = None,
            max_depth: Union[int, None] = None,
            print_progress_bar: bool = False
    ) -> Tuple[Union[List[str], None], int]:
        """
        Perform the A* search algorithm.

        :param initial_state: The initial state of the game.
        :param max_forward_model_calls: Maximum number of node expansions to avoid infinite loops.
        :param max_depth: Maximum depth for algorithms like DFS.
        :param print_progress_bar: if True, there will be a progress-bar in the console for the solving-attempt.
        :return: List of actions that lead to a solution (if found, else None), and the number of node expansions.
        """
        # Priority queue: (f(n), g(n), current_state, actions_so_far)
        # f(n) = g(n) + h(n) where g(n) is the path cost and h(n) is the heuristic estimate

        ctx = {
            "initial GameState": initial_state,
            "initial rules": set(initial_state.rules)
        }

        pq = []
        index = 0  # Unique index to ensure tuples are compared correctly
        heapq.heappush(pq, (self.heuristic.run(initial_state, ctx), 0, index, initial_state, []))

        visited = set()
        for i in range_or_infinite_loop(max_forward_model_calls, print_progress_bar):
            if not pq:
                break
            f, g, _, current_state, actions = heapq.heappop(pq)

            # Check if we have won the game
            if check_win(current_state):
                return actions, i

            # Serialize the state to check for duplicates
            state_str = current_state.unique_str()
            if state_str in visited:
                continue
            visited.add(state_str)

            # Expand the node: explore all possible actions
            for action in [Direction.Up, Direction.Down, Direction.Left, Direction.Right, Direction.Wait]:
                next_state = advance_game_state(action, current_state.copy())
                if next_state.unique_str() not in visited:
                    # g(next) is the cost so far plus 1 (since each move costs 1)
                    new_g = g + 1
                    # f(next) = g(next) + h(next)
                    new_f = new_g + self.heuristic.run(next_state, ctx)
                    index += 1  # Increment the index to maintain uniqueness

                    heapq.heappush(pq, (new_f, new_g, index, next_state, actions + [action.name]))

        return None, max_forward_model_calls  # Return empty if no solution is found

    class AStarFactory(AgentFromPolicy):
        def make_agent_from_policy(self, policy: Heuristic) -> AIInterface:
            return AStar(policy)


if __name__ == '__main__':
    from Keke_PY.keke_game.simulation import load_level_set, parse_map, map_to_string, make_level
    level_set = load_level_set("json_levels/full_biy_LEVELS.json")
    astar_agent = AStar(heuristic=SimpleHeuristic())

    demo_levels = level_set["levels"]
    for level in demo_levels:
        game_map = parse_map(level["ascii"])
        print(map_to_string(game_map))

        game_state = make_level(game_map)

        solution = astar_agent.search(game_state, 1000, None, True)
        print(solution)
