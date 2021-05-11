import random
import numpy as np
import copy
import matplotlib.pyplot as plt

smp = 5    # seeking memory pool
srd = 2     # seeking range of the selected dimension
cdc = 10    # counts of dimension to change
spc = True  # self-position considering
mr = 0.30   # mixture ratio
cats_num = 50 # number of cats
operations_num = 100
machines_num = 10
iterations = 1000

class Cat:

    def __init__(self, operations):
        self.position = operations

    def fitness(self):
        # FIXME this doesn't calculate fitness properly
        machines =  [Machine() for i in range(0, machines_num)]
        machines_op = [[] for _ in machines]
        for operation in self.position:
            machines_op[operation.machine - 1].append(operation)
        while list(filter(lambda machine_op: machine_op != [], machines_op)) != []:
            for i in range(0, len(machines)):
                if machines_op[i] != []:
                    operation = machines_op[i].pop(0)
                    wait_time = 0
                    for j in range(0, len(machines)):
                        if j != i:
                            if machines[j].current_operation != None and machines[j].current_operation.job == operation.job:
                                wait_time = machines[j].time - machines[i].time
                                break
                    machines[i].current_operation = operation
                    machines[i].time += (wait_time + operation.time)
        machines.sort(key=lambda machine: machine.time, reverse=True)
        return machines[0].time

    def apply_mode(self):
        if self.sm:
            self.__apply_sm()
        else:
            self.__apply_tm()

    def __apply_sm(self):
        cat_copies = []
        j = smp
        if spc:
            j = smp - 1
            cat_copies.append(self)

        for i in range(0, j):
            cat_copies.append(copy.deepcopy(self))

        for cat in cat_copies:
            srd = random.randrange(0, operations_num)

            if (srd+cdc > operations_num):
                mutation = cat.position[srd - (len(cat.position) - cdc):srd+1]
                mutation = mutation[::-1]
                new_position = cat.position[0:srd - (len(cat.position) - cdc)] + mutation + cat.position[srd+1:]
                assert len(new_position) == operations_num
                cat.position = new_position
            else:
                mutation = cat.position[srd+1:srd+cdc]
                mutation = mutation[::-1]
                new_position = cat.position[0:srd+1] + mutation + cat.position[srd+cdc:]
                assert len(new_position) == operations_num
                cat.position = new_position

        # TODO select by probability
        self_fitness = self.fitness()
        for cat in cat_copies:
            new_fitness = cat.fitness()
            if new_fitness < self_fitness:
                self.position = cat.position
                break


    def __apply_tm(self):
        #TODO implement tracing mode
        pass


class Operation:
    def __init__(self, job, machine, time):
        self.job = job
        self.machine = machine
        self.time = time

    def __repr__(self):
        return "<Operation job:%s, machine:%s, time:%s>" % (self.job, self.machine, self.time)


class Machine:
    def __init__(self):
        self.time = 0
        self.current_operation = None


def read_input():
    times = np.genfromtxt("./times.csv", dtype=int, delimiter=",")
    machines = np.genfromtxt("./machines.csv", dtype=int, delimiter=",")
    return times, machines

def parse_input(times, machines):
    jobs = times.shape[0] # number of rows == number of jobs
    operations = []
    for x, y in np.ndindex(times.shape):
        operation = Operation(x % jobs + 1, machines[x, y], times[x, y])
        operations.append(operation)
    return operations

def main():
    times, machines = read_input()
    operations = parse_input(times, machines)
    best_fitnesses = []
    best_fitness = None
    best_position = None
    cats = []
    for i in range(0, cats_num):
        operations = copy.deepcopy(operations)
        random.shuffle(operations)
        cats.append(Cat(operations))

    for i in range(0, iterations):
        print("Iteration %d" % i)
        for cat in cats:
            sm = random.random() > mr
            cat.sm = sm
            new_fitness = cat.fitness()
            if best_fitness == None or new_fitness < best_fitness:
                best_fitness = new_fitness
                best_position = cat.position

        best_fitnesses.append(best_fitness)

        for cat in cats:
            cat.apply_mode()

        print("Best fitness %d" % best_fitness)

    x_axis = [i for i in range(0, iterations)]
    plt.plot(x_axis,  best_fitnesses)
    plt.show()

def test_fitness():
    o1 = Operation(1, 3, 2)
    o2 = Operation(1, 1, 3)
    o3 = Operation(1, 2, 5)
    o4 = Operation(2, 1, 5)
    o5 = Operation(2, 3, 7)
    o6 = Operation(2, 2, 1)
    o7 = Operation(3, 1, 4)
    o8 = Operation(3, 2, 5)
    o9 = Operation(3, 3, 1)
    operations = [o7, o5, o3, o2, o9, o1, o6, o4, o8]
    cat = Cat(operations)
    assert cat.fitness == 13

if __name__ == "__main__":
    main()

