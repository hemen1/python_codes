import numpy as np
from ACO import ACO

distance_matrix = np.loadtxt('distance_matrix.txt', delimiter=' ')

aco = ACO(distance_matrix, 1, 28, iteration=100, n_ant=60)
best_path, dist_min_cost = aco.solve()
print(best_path, "\n", dist_min_cost)
