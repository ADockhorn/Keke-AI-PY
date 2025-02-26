from typing import List

with open("Keke_PY/evaluation/single_level_optimization_combined_logs.txt") as file:
    lines: List[str] = file.readlines()


solving_matrix: List[List[bool]] = []

for line in lines:
    if line.startswith("LEVEL AGENT EVALUATION:"):
        _, *results = line.split(':')
        solving_matrix.append([result.strip() != "----" for result in results])


for row in solving_matrix:
    print(*row)