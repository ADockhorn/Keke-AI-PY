from Keke_PY.heuristic_representations.SingleObjRepresentation import SingleObjRepresentation
from Keke_PY.heuristics.HeuristicTree import HeuristicTree, create_random_tree, mutation, crossover
from Keke_PY.heuristics.ParametrisedHeuristic import Heuristic


class HeuristicTreeRepresentation(SingleObjRepresentation[HeuristicTree]):

    max_depth: int
    def __init__(self, max_depth: int = 10):
        self.max_depth = max_depth


    def _assert_type(self, x: object) -> HeuristicTree:
        assert isinstance(x, HeuristicTree)
        return x

    def _into_heuristic(self, x: HeuristicTree) -> Heuristic:
        return x

    def _serialize(self, x: HeuristicTree) -> str:
        return ';'.join(map(str, x.to_data()))

    def _deserialize(self, x: str) -> HeuristicTree:
        return HeuristicTree.from_data(iter(x.split(';')))

    def _sample(self) -> HeuristicTree:
        return create_random_tree(self.max_depth)

    def _mutate(self, x: HeuristicTree) -> HeuristicTree:
        return mutation(x, self.max_depth)

    def _crossover(self, x: HeuristicTree, y: HeuristicTree) -> HeuristicTree:
        return crossover(x, y, self.max_depth)

    def _are_equal(self, x: HeuristicTree, y: HeuristicTree) -> bool:
        return x == y