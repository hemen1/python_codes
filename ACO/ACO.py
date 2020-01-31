import numpy as np

class _ant:
    def __init__(self, start):
        self.start = start
        self.position = start
        self.map_mat = [start]

    def reset(self):
        self.position = self.start
        self.map_mat = [self.start]

    def get_position(self):
        return self.position

    def set_next(self, next_position):
        self.position = next_position
        self.map_mat.append(next_position)


class ACO:
    def __init__(self, distance_matrix, start, end, max_dist=None,
                 n_ant=None, alpha=1, beta=2, iteration=100, e=0.5):
        self.distance_matrix = distance_matrix
        self.start = start
        self.end = end
        self.max_dist = 0 if max_dist is None else max_dist
        self.n_ant = len(distance_matrix) if n_ant is None else n_ant
        self.alpha = alpha
        self.beta = beta
        self.iteration = iteration
        self.e = e
        self.visibility = 1 / distance_matrix
        self.visibility[self.visibility == np.inf] = 0


    def solve(self):
        self.ants = [_ant(self.start) for i in range(self.n_ant)]
        pheromne = np.ones_like(self.distance_matrix)*0.1

        for ite in range(self.iteration):

            for i in range(self.n_ant):
                temp_visibility = np.array(self.visibility)  # creating a copy of visibility
                self.ants[i].reset()
                while True:
                    cur_loc = self.ants[i].get_position()  # current city of the ant

                    temp_visibility[:, cur_loc] = 0  # making visibility of the current city as zero

                    p_feature = np.power(pheromne[cur_loc, :], self.beta)  # calculating pheromne feature
                    v_feature = np.power(temp_visibility[cur_loc, :], self.alpha)  # calculating visibility feature

                    p_feature = p_feature[:, np.newaxis]  # adding axis to make a size[None,1]
                    v_feature = v_feature[:, np.newaxis]  # adding axis to make a size[None,1]

                    combine_feature = np.multiply(p_feature, v_feature)  # calculating the combine feature

                    total = np.sum(combine_feature)  # sum of all the feature

                    probs = combine_feature / total  # finding probability of element probs(i) = comine_feature(i)/total
                    cum_prob = np.cumsum(probs)  # calculating cummulative sum
                    # print(cum_prob)
                    r = np.random.random_sample()  # randon no in [0,1)
                    # print(r)
                    node = np.nonzero(cum_prob >= r)[0][
                        0]  # finding the next node having probability higher then random(r)

                    self.ants[i].set_next(node)  # adding city to route
                    if node == self.end:
                        break
                    if len(self.ants[i].map_mat) >= len(self.distance_matrix) - 1:
                        self.ants[i].set_next(self.end)
                        break

            dist_cost = np.zeros((self.n_ant, 1))  # intializing total_distance_of_tour with zero

            for i in range(self.n_ant):

                s = 0
                for j in range(len(self.ants[i].map_mat)-1):
                    s = s + self.distance_matrix[int(self.ants[i].map_mat[j]),
                                                 int(self.ants[i].map_mat[j + 1])]  # calcualting total tour distance

                dist_cost[i] = s  # storing distance of tour for 'i'th ant at location 'i'

            dist_min_loc = np.argmin(dist_cost)  # finding location of minimum of dist_cost
            dist_min_cost = dist_cost[dist_min_loc]  # finging min of dist_cost

            best_route = self.ants[dist_min_loc].map_mat  # intializing current traversed as best route
            pheromne = (1 - self.e) * pheromne  # evaporation of pheromne with (1-e)

            if dist_min_cost < self.max_dist:
                return best_route, dist_min_cost

            for i in range(self.n_ant):
                dt = 1 / dist_cost[i]
                for j in range(len(self.ants[i].map_mat)-1):
                    pheromne[int(self.ants[i].map_mat[j]), int(self.ants[i].map_mat[j + 1])] = \
                        pheromne[int(self.ants[i].map_mat[j]), int(self.ants[i].map_mat[j + 1])] + dt
                    # updating the pheromne with delta_distance
                    # delta_distance will be more with min_dist i.e adding more weight to that route  peromne
            print('itr =', ite, ' dist min cost=', dist_min_cost)
        return best_route, dist_min_cost
