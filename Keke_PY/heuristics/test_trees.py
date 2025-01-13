import pickle

from Keke_PY.heuristics.HeuristicTree import HeuristicTree
from Keke_PY.heuristics.gpmodule import create_random_tree, mutation

if __name__ == "__main__":

    random_tree = create_random_tree(10)



    dump_file_name: str = "test_trees.pickle"

    with open(dump_file_name, "wb") as file:
        pickle.dump(list(random_tree.to_data()), file)

    with open(dump_file_name, "rb") as file:
        loaded_data = pickle.load(file)

    loaded_tree = HeuristicTree.from_data(iter(loaded_data))

    print(random_tree == loaded_tree)
    print(random_tree)
    print(loaded_tree)
    print(loaded_data)
    print(mutation(random_tree, 10))
    print(random_tree)