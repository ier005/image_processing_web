#!/usr/bin/env python


# configure variables
g = 7
p = 3
w = 10
tabu_list_length = 20
random_swap_length = 4
pernalty_value = w


import time
from random import sample
from random import randint


# global variables
person_list = {i for i in range(g*p)}
person_freedom_list = {}
#person_freedom_priority = []
freedom_list = []
penalty_list = []
conf = []
best_so_far = float('inf')
current_target = float('inf')
no_improve_count = 0

class Week():
    def __init__(self):
        self.persons = set()
        self.conf = []
        self.tabu_list = [None] * tabu_list_length
        self.tabu_list_index = 0
        self.conflict_list = set()

def initFreedomList():
    person_num = g * p
    for i in range(person_num):
        person_freedom_list[i] = person_list.copy()
        person_freedom_list[i].remove(i)
    '''
    for i in range(person_num):
        person_freedom_priority.append((i, person_num - 1))
    '''
    for i in range(person_num):
        for j in range(i+1, person_num):
            freedom_list.append(({i, j}, person_num - 2))


def insertFreedom(node, l):
    if len(l) == 0:
        l.append(node)
        return
    ind = -1
    for i in range(len(l)):
        if l[i][1] < node[1]:
            ind = i
            break
    if ind == -1:
        ind = len(l)
    l.insert(ind, node)

def chooseNode(node, group):
    penalty_list.append(node[0])
    for i in group:
        for j in node[0]:
            person_freedom_list[i].discard(j)
    for i in node[0]:
        for j in group:
            person_freedom_list[i].discard(j)
    for i in node[0]:
        for j in node[0]:
            person_freedom_list[i].discard(j)

    person_num = g * p
    '''
    l = []
    for i in range(person_num):
        insert_person((i, len(person_freedom_list[i])), l)
    global person_freedom_priority
    person_freedom_priority = l
    '''
    l = []
    for i in range(person_num):
        for j in range(i+1, person_num):
                n = ({i, j}, len(person_freedom_list[i] & person_freedom_list[j]) - (pernalty_value if {i, j} in penalty_list else 0))
                insertFreedom(n, l)
    global freedom_list
    freedom_list = l

'''
def insert_person(p, l):
    if len(l) == 0:
        l.append(p)
        return
    ind = -1
    for i in range(len(l)):
        if l[i][1] < p[1]:
            ind = i
            break
    if ind == -1:
        ind = len(l)
    l.insert(ind, p)
'''

def choosePerson(person, group):
    for i in group:
        penalty_list.append({i, person})
        person_freedom_list[i].discard(person)
        person_freedom_list[person].discard(i)

    person_num = g * p
    '''
    l = []
    for i in range(person_num):
        insert_person((i, len(person_freedom_list[i])), l)
    global person_freedom_priority
    person_freedom_priority = l
    '''
    l = []
    for i in range(person_num):
        for j in range(i+1, person_num):
                n = ({i, j}, len(person_freedom_list[i] & person_freedom_list[j]) - (pernalty_value if {i, j} in penalty_list else 0))
                insertFreedom(n, l)
    global freedom_list
    freedom_list = l
    

def arrangeWeek(week):
    for i in range(g):
        mod = p % 2
        group = set()
        for j in range(p // 2):
            for node in freedom_list:
                if len(node[0] & week.persons) == 0:
                    week.persons.update(node[0])
                    chooseNode(node, group)
                    group.update(node[0])
                    break
            if mod:
                tem_set = person_list - week.persons
                person = sample(tem_set, 1)[0]
                week.persons.add(person)
                choosePerson(person, group)
                group.add(person)
                break
        week.conf.append(group)


def initConf():
    for i in range(w):
        week = Week()
        arrangeWeek(week)
        conf.append(week)



def calculateTarget():
    positions = set()
    for i in range(len(conf)):
        week = conf[i]
        for n in range(len(week.conf)):
            tem_set = []
            for k in week.conf[n]:
                for l in week.conf[n]:
                    if k == l or {k, l} in tem_set:
                        continue
                    tem_set.append({k, l})
                    for j in range(i+1, len(conf)):
                        week1 = conf[j]
                        for m in range(len(week1.conf)):
                            if k in week1.conf[m] and l in week1.conf[m]:
                                #print('week {}, {} | week {}, {}'.format(i, week.conf[n], j, week1.conf[m]))
                                positions.update({(i, n, k), (i, n, l), (j, m, k), (j, m, l)})
                                
    #print("{} positions are conflict".format(len(positions)))
    return len(positions)

def findConflict():
    for week in conf:
        week.conflict_list = set()
    for i in range(len(conf)):
        week = conf[i]
        for n in range(len(week.conf)):
            tem_set = []
            for k in week.conf[n]:
                for l in week.conf[n]:
                    if k == l or {k, l} in tem_set:
                        continue
                    tem_set.append({k, l})
                    for j in range(i+1, len(conf)):
                        week1 = conf[j]
                        for m in range(len(week1.conf)):
                            if k in week1.conf[m] and l in week1.conf[m]:
                                week.conflict_list.add((n, k))
                                week.conflict_list.add((n, l))
                                week1.conflict_list.add((m, k))
                                week1.conflict_list.add((m, l))
    count = 0
    for week in conf:
        count += len(week.conflict_list)
    print("Current conflict: {}".format(count))

def swap(week, p1, p2):
    week.conf[p1[0]].remove(p1[1])
    week.conf[p1[0]].add(p2[1])
    week.conf[p2[0]].remove(p2[1])
    week.conf[p2[0]].add(p1[1])

def findNextChange():
    best = (None, float('inf'))
    for week in conf:
        for position in week.conflict_list:
            for i in range(len(week.conf)):
                if i == position[0]:
                    continue
                for j in week.conf[i]:
                    swap(week, position, (i, j))
                    res = calculateTarget()
                    if res < best[1]:
                        if {position[1], j} not in week.tabu_list or res < best_so_far:
                            best = ((week, position, (i, j)), res)
                    swap(week, (position[0], j), (i, position[1]))
    return best

def updateConf(change):
    week, p1, p2 = change[0], change[1], change[2]
    swap(week, p1, p2)
    pair = {p1[1], p2[1]}
    if pair not in week.tabu_list:
        week.tabu_list[week.tabu_list_index % tabu_list_length] = pair
        week.tabu_list_index += 1


def randomChange():
    print('No improvement for 4 iters, random change')
    for i in range(2):
        index = randint(0, w-1)
        group1 = randint(0, g-1)
        group2 = randint(0, g-1)
        while group2 == group1:
            group2 = randint(0, g-1)
        
        week = conf[index]
        m = sample(week.conf[group1], 1)[0]
        n = sample(week.conf[group2], 1)[0]
        pair = {m, n}
        if pair not in week.tabu_list:
            week.tabu_list[week.tabu_list_index % tabu_list_length] = pair
            week.tabu_list_index += 1
        swap(week, (group1, m), (group2, n))

def localSearch():
    global current_target
    global best_so_far
    global no_improve_count

    if calculateTarget() == 0:
        return True
    change, res = findNextChange()
    if change == None:
        print('No option to move!!')
        exit()
    if res < current_target:
        no_improve_count = 0
    else:
        no_improve_count += 1

    updateConf(change)
    current_target = res
    if current_target < best_so_far:
        best_so_far = current_target

    if no_improve_count >= 4:
        randomChange()
        no_improve_count = 0
    findConflict()
    


if __name__ == '__main__':
    t = time.process_time()

    initFreedomList()
    initConf()
    for week in conf:
        print(week.conf)
    #print(freedom_list)
    #print(person_freedom_list)
    print("[Time] Init done:", time.process_time()-t)

    findConflict()

    while not localSearch():
        pass
    for week in conf:
        print(week.conf)

    print("[Time] Used totally:", time.process_time()-t)