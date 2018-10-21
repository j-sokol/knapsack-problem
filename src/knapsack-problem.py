#!/usr/bin/env python3

import sys
from itertools import combinations
import time

measured_time = []

def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        # print('{:s} function took {:.3f} ms'.format(f.__name__, (time2-time1)*1000.0))
        measured_time.append({'type': f.__name__, 'time': (time2-time1)*1000.0})
        return ret
    return wrap



class InstanceSolution(object):
    def __init__(self, **kwargs):
        super(InstanceSolution, self).__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

        if hasattr(self, 'solution_line'):

            parsed_solution = self.solution_line.split(" ")
            self.id = int(parsed_solution[0])
            self.no_items = int(parsed_solution[1])
            self.best_cost = int(parsed_solution[2])
            self.best_combination = [int(i) for i in parsed_solution[4:]]
        


    def __eq__(self, other):
        return (self.no_items, self.best_cost, self.best_combination) == (other.no_items, other.best_cost,other.best_combination)

    def __repr__(self):
        return "{} {} {}".format(str(self.no_items), str(self.best_cost), str(self.best_combination))

    def get_id(self):
        return self.id

    def get_no_items(self):
        return self.no_items

    def get_cost(self):
        return self.best_cost

    def get_solution_line(self):
        return self.no_items, self.best_cost, self.best_combination


class Instance(object):
    def __init__(self, instance_line):
        super(Instance, self).__init__()
        parsed_instance = instance_line.split(" ")
        self.id = int(parsed_instance[0])
        self.no_items = int(parsed_instance[1])
        self.capacity = int(parsed_instance[2])
        self.items = []
        for index, (weight, price) in enumerate(zip(parsed_instance[3::2], parsed_instance[4::2])):
            # self.items.append((int(weight), int(price)))
            self.items.append({"id": index, "weight": int(weight), "price": int(price), "entered": False})

        
    def get_items(self):
        return self.items

    def get_id(self):
        return self.id

    @timing
    def brute_force(self):
        capacity = self.capacity
        weight_cost = self.items
        best_cost = None
        best_combination = []
        # generating combinations by all ways: C by 1 from n, C by 2 from n, ...
        for way in range(self.no_items):
            for comb in combinations(weight_cost, way + 1):
                weight = sum([wc['weight'] for wc in comb])
                cost = sum([wc['price'] for wc in comb])
                if (best_cost is None or best_cost < cost) and weight <= capacity:
                    best_cost = cost
                    best_combination = [0] * self.no_items
                    for wc in comb:
                        best_combination[weight_cost.index(wc)] = 1

        return InstanceSolution(no_items=self.no_items, best_cost=best_cost, best_combination=best_combination)

    @timing
    def with_heuristic(self):

        # Sort objects by decreasing price
        sorted_by_price_items = sorted(self.items, key=lambda x: x['price'], reverse=True)

        best_combination = {el:0 for el in range(len(sorted_by_price_items))}
        
        current_price = 0
        current_weight = 0

        for index, item in enumerate(sorted_by_price_items):
            
                if (current_weight + item['weight']) > self.capacity:
                    continue

                current_price += item['price'];
                current_weight += item['weight'];
                best_combination[sorted_by_price_items[index]['id']] = 1

                if current_weight == self.capacity:
                    break
        return InstanceSolution(no_items=self.no_items, best_cost=current_price, best_combination=list(best_combination.values()))




def main(argv):
    # print (argv[1:], type (argv[1]))

    try:
        instance_file = open(argv[2], "r")
        solution_file = open(argv[3], "r")
        mode = argv[1]
        if mode != "-s" and mode != "-e":
            print ("test")
            raise Exception('Wrong mode.')
    except:
        print("Instance and/or solution file not passed as parameter.\n",
               "Usage:", argv[0], "-e/-s <instance_file> <solution_file>\n",
               "    -e measures relative error compared to the reference solution\n",
               "    -s measures speed of both brute force and heuristic computations") 
        return 1


    instances = {}
    solutions = {}
    relative_errors = []

    for solution_line in solution_file:
        solution = InstanceSolution(solution_line=solution_line.rstrip('\n'))
        solutions.update({solution.get_id(): solution})

    for instance_line in instance_file:
        instance = Instance(instance_line.rstrip('\n'))
        instances.update({instance.get_id(): instance})


    backpack_size = next(iter(solutions.values())).get_no_items()

    # Measure speed mode
    if mode == "-s":
        for id_inst, instance in instances.items():

            brute_force = instance.brute_force()
            heuristic = instance.with_heuristic()

        # # Create CSV with measured times
        print("{}.brute_force,{}.heuristic".format(backpack_size, backpack_size))
        for brute_force, heuristic in zip(measured_time[3::2], measured_time[4::2]):
            print (brute_force['time'], ",", heuristic['time'], sep='')



    # Relative error mode
    if mode == "-e":

        print("{}.relative_error".format(backpack_size))


        for id_inst, instance in instances.items():
            heuristic = instance.with_heuristic()
            relative_error = (solutions[id_inst].get_cost() - heuristic.get_cost())/solutions[id_inst].get_cost()
            print(relative_error)

    # print("Relative error across all instances: ", sum(relative_errors)/float(len(relative_errors)))


    

if __name__ == "__main__":
    main(sys.argv)