import numpy as np
import copy


class course:
    """ course details """

    def __init__(self, name, course_id, lecturer_id, groupe, time_per_week, is_lab=False):
        self.name = name  # name of course
        self.course_id = course_id  # id of course
        self.lecturer_id = lecturer_id  # id of lecturer
        self.is_lab = is_lab  # is lab course or no
        self.time_per_week = time_per_week  # times of course in week
        self.groupe = groupe  # course id

    def __str__(self):
        string_out = ''
        if self.is_lab:
            string_out += "lab : "
        else:
            string_out += "      "
        string_out += "name :" + self.name + " course ID:" + str(self.course_id) + \
                      "  lecturer id:" + str(self.lecturer_id) + " groupe:" + str(self.groupe)
        return string_out


class room:
    """ rooms details """

    def __init__(self, name, is_lab=False):
        self.name = name  # room name
        self.is_lab = is_lab  # is room use for lab or no


class member:
    """ member is an time slop that contain time slop for each room"""

    class Chromosome:
        """ chromosome is an time slop for a room"""

        def __init__(self, days=5, time=4, is_lab=False):
            self.is_lab = is_lab
            self.time_slop = -1 * np.ones((days, time), dtype=np.int)

    def __init__(self, course_list, rooms_list, days=5, time=4, init=False):
        self.course_list = course_list
        self.room_number = len(rooms_list)
        self.rooms = rooms_list
        self.days = days
        self.time = time
        self.cost = None
        self.chromosomes = [self.Chromosome(days=days, time=time, is_lab=room.is_lab) for room in rooms_list]
        if init:
            self.init_chromosomes()

    def init_chromosomes(self):
        # init member by random for each course
        for i in range(len(self.course_list)):
            for j in range(self.course_list[i].time_per_week):
                count = 0
                while count < 10:
                    room_random = np.random.randint(0, self.room_number)  # get random room number
                    gene_day_number = np.random.randint(0, self.days)  # get random day number
                    gene_time_number = np.random.randint(0, self.time)  # get random time number
                    if self.chromosomes[room_random].time_slop[gene_day_number, gene_time_number] == -1:
                        self.chromosomes[room_random].time_slop[gene_day_number, gene_time_number] = i
                        break
                    count += 1

    def cost_fun(self):
        """ calculation cost of each member """
        self.cost = 0
        # calculation cost for lab rooms
        # if course is lab and room is not lab or course is not lab and room is lab
        # cost increase
        for room in self.chromosomes:
            for i in range(self.days):
                for j in range(self.time):
                    if room.time_slop[i, j] != -1:
                        if self.course_list[room.time_slop[i, j]].is_lab != room.is_lab:
                            self.cost += 2
        # calculation cost for lecturer
        # if lecturer of course is repeated in same time at day
        # cost increase
        for i in range(self.days):
            for j in range(self.time):
                seen_lecturer_id = []
                for room in self.chromosomes:
                    if room.time_slop[i, j] != -1:
                        lecturer_id = self.course_list[room.time_slop[i, j]].lecturer_id
                        if lecturer_id in seen_lecturer_id:
                            self.cost += 1
                        else:
                            seen_lecturer_id.append(lecturer_id)
        # calculation cost for time per week
        # if time per week of course is not same with time table
        # cost increase
        course_time_repeated_in_week = {i: 0 for i in range(len(self.course_list))}
        for room in self.chromosomes:
            for i in range(self.days):
                for j in range(self.time):
                    if room.time_slop[i, j] != -1:
                        if room.time_slop[i, j] in course_time_repeated_in_week.keys():
                            course_time_repeated_in_week[room.time_slop[i, j]] += 1
                        else:
                            course_time_repeated_in_week[room.time_slop[i, j]] = 1
        for i in range(len(self.course_list)):
            if self.course_list[i].time_per_week != course_time_repeated_in_week[i]:
                self.cost += abs(self.course_list[i].time_per_week - course_time_repeated_in_week[i])

    def reset_cost(self):
        self.cost = None

    def get_cost(self):
        # get cost of member
        if self.cost is None:
            self.cost_fun()
        return self.cost

    def __str__(self):
        """ create time table for print in out put """
        time_list = ["8:00 -> 10:00", "10:00 -> 12:00", "14:00 -> 16:00", "16:00 -> 18:00"]
        day_list = ['sat', 'sun', "mon", "tue", 'wed', "thu", 'fri']
        out_string = ""
        for k in range(self.room_number):

            out_string += "\n"
            if self.rooms[k].is_lab:
                out_string += " lab :"
            out_string += str(self.rooms[k].name) + "\n ------------------------ \n"
            for i in range(self.days):
                for j in range(self.time):
                    if self.chromosomes[k].time_slop[i, j] != -1:
                        out_string += day_list[i] + "  " + time_list[j] + "  " + str(
                            self.course_list[self.chromosomes[k].time_slop[i, j]]) + "\n"

        return out_string


class GA:
    """ genetic algorithm for solve this problem """

    def __init__(self, iteration, population_number, course_list, room_list, crossover_rate=0.8, mutation_rate=0.1,
                 days=5, time=4):
        self.iterarion = iteration
        self.population_number = population_number
        self.course_list = course_list
        self.room_list = room_list
        self.room_number = len(room_list)
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.days = days
        self.time = time
        self.members = [member(self.course_list, self.room_list, self.days, self.time, init=True) for i in
                        range(self.population_number)]

    def solve(self):
        """ solve GA"""
        best_cost = np.inf
        for ite in range(self.iterarion):
            costs = [self.members[i].get_cost() for i in range(self.population_number)]
            costs = np.asarray(costs)
            argsort_costs = costs.argsort()
            self.members = sorted(self.members, key=lambda member: member.get_cost())
            self.members = self.members[:self.population_number]

            crossover_result = self.crossover()
            mutation_result = self.mutation()
            for child in crossover_result:
                self.members.append(child)

            for mutated in mutation_result:
                self.members.append(mutated)

            costs = [self.members[i].get_cost() for i in range(self.population_number)]
            costs = np.asarray(costs)
            argsort_costs = costs.argsort()
            self.members = sorted(self.members, key=lambda member: member.get_cost())
            self.members = self.members[:self.population_number]
            costs = costs[argsort_costs]
            if costs[0] <= best_cost:
                best_cost = copy.deepcopy(costs[0])
                best_solotion = copy.deepcopy(self.members[0])
            print("best cost :", best_cost, " at iteration :", ite)
        return best_solotion, best_cost

    def crossover(self):
        """ crossover the population by select 2 parent and create 2 children"""
        children = []
        random_choice = np.random.choice(self.members, (int(self.population_number / 2), 2), replace=False)
        for choice in random_choice:
            if np.random.random() < self.crossover_rate:
                child1 = copy.deepcopy(choice[0])
                child2 = copy.deepcopy(choice[1])
                child1.reset_cost()
                child2.reset_cost()
                temp = copy.deepcopy(child1)
                change_matrix = np.random.random_integers(0, 1, (self.room_number, self.days, self.time))
                for i in range(self.room_number):
                    for j in range(self.days):
                        for k in range(self.time):
                            if change_matrix[i, j, k] == 1:
                                child1.chromosomes[i].time_slop[j, k] = child2.chromosomes[i].time_slop[j, k]
                                child2.chromosomes[i].time_slop[j, k] = temp.chromosomes[i].time_slop[j, k]

                children.append(child1)
                children.append(child2)

        return children

    def mutation(self):
        """ mutation the population by select a population"""
        mutations = []
        for p in range(self.population_number):
            if np.random.random() < self.mutation_rate:
                mutations.append(self._mutation(p))

        return mutations

    def _mutation(self, p):
        child = copy.deepcopy(self.members[p])
        child.reset_cost()
        change_matrix = np.random.random_integers(0, 1, (self.room_number, self.days, self.time))
        for i in range(self.room_number):
            for j in range(self.days):
                for k in range(self.time):
                    if change_matrix[i, j, k] == 1:
                        child.chromosomes[i].time_slop[j, k] = np.random.random_integers(0, len(
                            self.course_list) - 1)
                        return child
        return child
