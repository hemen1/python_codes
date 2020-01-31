import numpy as np
from class_schedule import GA, course, room

courses = np.loadtxt('class.txt', dtype=np.str, delimiter=',')
rooms = np.loadtxt('rooms.txt', dtype=np.str, delimiter=',')

course_list = []
for i in courses:
    course_list.append(course(name=i[0], course_id=int(i[1]), lecturer_id=int(i[2]),
                              groupe=int(i[3]), time_per_week=int(i[4]), is_lab=bool(int(i[5]))))

room_list = []
for i in rooms:
    room_list.append(room(i[0], bool(int(i[1]))))

ga = GA(500, 200, course_list, room_list, days=3, time=4)
best_solotion, best_cost = ga.solve()
print(best_cost)
print(best_solotion)
