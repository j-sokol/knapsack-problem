#!/usr/bin/env python3

import sys
from itertools import combinations
import time
from math import floor

import numpy as np
from copy import copy


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


        # print("Parsed cap:", parsed_instance)
        for index, (weight, price) in enumerate(zip(parsed_instance[3::2], parsed_instance[4::2])):
            # self.items.append((int(weight), int(price)))
            self.items.append({"id": index, "weight": int(weight), "price": int(price), "entered": False})

        self.selected_items = []
        self.selected_price = 0
        
    def get_items(self):
        return self.items

    def get_capacity(self):
        return self.capacity


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




    def solve_branch_bound(self, used_items, current_price, current_weight, remaining_prices):
        # if max depth was reached
        if len(used_items) == self.no_items:
            return

        # Better results are not possible
        possible_price = current_price + remaining_prices[len(used_items)]
        if possible_price < self.selected_price:
            return

        # With next item
        new_price = current_price + self.items[len(used_items)]['price']
        new_weight = current_weight + self.items[len(used_items)]['weight']

        # Check if weight is under capacity
        if new_weight <= self.capacity:
            # Breaking new best
            if new_price > self.selected_price:
                self.selected_items = used_items + [1]
                self.selected_price = new_price
            self.solve_branch_bound(used_items + [1],
                                    new_price,
                                    new_weight, 
                                    remaining_prices)

        # Without next item
        self.solve_branch_bound(used_items + [0],
                                current_price,
                                current_weight, 
                                remaining_prices)
        pass

    @timing
    def branch_bound(self):
        selected_price = 0
        selected_items = []

        # Create list of remaining prices
        remaining_prices = [0] * self.no_items
        remaining_prices[self.no_items-1] = self.items[self.no_items-1]['price']

        for i in range(self.no_items-1-1, 0, -1):
            remaining_prices[i] = remaining_prices[i+1] + self.items[i]['price']

        self.solve_branch_bound([], 0, 0, remaining_prices)

        # Append zeros to the output
        while len(self.selected_items) < self.no_items:
            self.selected_items.append(0)

        return InstanceSolution(no_items=self.no_items, best_cost=self.selected_price, best_combination=self.selected_items)

    def get_from_decomposition_table(self, decomposition_table, total_price, total_weight, item_id):

        if item_id >= len(self.items):
            return

        decomposition_table[item_id][total_price] = total_weight

        if item_id + 1 < len(self.items):
            next_item = self.items[item_id+1]
            next_price = total_price + next_item['price']
            next_weight = total_weight + next_item['weight']

            # If weight with next item is under capacity, add it
            if next_weight <= self.capacity:
                self.get_from_decomposition_table(decomposition_table, next_price, next_weight, item_id+1)
      
            self.get_from_decomposition_table(decomposition_table, total_price, total_weight, item_id+1)
        pass

    @timing
    def dynamic(self):
        return self.dynamic2()

    def dynamic2(self):
        # Collumns
        max_cost = sum([x['price'] for x in self.items]) + 1

        # Rows
        item_rows = len(self.items)

        # Get first item to work with
        item = self.items[0]

        # Create decomposition table
        decomposition_table = np.zeros((item_rows, max_cost))

        self.get_from_decomposition_table(decomposition_table, item['price'], item['weight'], 0)
        self.get_from_decomposition_table(decomposition_table, 0, 0, 0)

        # Remove all zeros at the end of the list
        last_row = decomposition_table[-1].tolist()
        while last_row[-1] == 0: 
            last_row = last_row[:-1]


        best_cost = len(last_row) - 1

        return InstanceSolution(no_items=np.nan, best_cost=best_cost, best_combination=[np.nan]*self.no_items)

    @timing
    def fptas(self, accuracy):

        # Count maximum price
        max_price = max([x['price'] for x in self.items])

        ratio = ((1.0 - accuracy) * max_price) / len(self.items)

        # Create new weighted list
        self.items = [{'id': i['id'], 'weight': i['weight'], 'price': floor(i['price'] / ratio)} for i in self.items]

        # Solve problem with dynamic programming
        dynamic = self.dynamic2()
        dynamic.best_cost = floor(dynamic.best_cost * ratio)

        return dynamic

def main(argv):

    try:
        instance_file = open(argv[2], "r")
        solution_file = open(argv[3], "r")
        mode = argv[1]
        if mode != "-s" and mode != "-e" and mode != "-fe" and mode != "-fs":
            print ("test")
            raise Exception('Wrong mode.')
    except:
        print("Instance and/or solution file not passed as parameter.\n",
               "Usage:", argv[0], "-e/-s <instance_file> <solution_file>\n",
               "    -e measures relative error compared to the reference solution\n",
               "    -s measures speed of both brute force and heuristic computations\n",
               "    -fe measures error FPTAS algorithm depending on accurancy\n",
               "    -fs measures speed of FPTAS algorithm depending on accurancy") 
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
            # brute_force = instance.brute_force()
            # heuristic = instance.with_heuristic()
            bb = instance.branch_bound()
            dynamic = instance.dynamic2()
            fptas = instance.fptas(0.75)
            # print ("He:", heuristic)
            # print ("Br:", brute_force)
            # print ("So:", solutions[id_inst])
            # print ("Dy:", dynamic)
            # print ("Fp:", fptas)
            # print ("Bb:", bb)

        # # Create CSV with measured times
        print("{}.brute_force,{}.bb,{}.dynamic,{}.fptas".format(backpack_size, backpack_size, backpack_size, backpack_size))
        for brute_force, bb, dynamic, fptas in zip(measured_time[3::4], measured_time[4::4], measured_time[5::4],measured_time[6::4]):
            print (np.nan, ",", bb['time'], ",", dynamic['time'], ",", fptas['time'], sep='')



    # Relative error mode
    if mode == "-e":

        print("{}.relative_error".format(backpack_size))


        for id_inst, instance in instances.items():
            heuristic = instance.with_heuristic()
            relative_error = (solutions[id_inst].get_cost() - heuristic.get_cost())/solutions[id_inst].get_cost()
            print(relative_error)

    # print("Relative error across all instances: ", sum(relative_errors)/float(len(relative_errors)))
    

    accuracies = [0.99, 0.9, 0.7, 0.5, 0.3]     

    # FPTAS error mode
    if mode == "-fe":

        print("{}.solution.value".format(backpack_size), end=",")
        for accuracy in accuracies:
            print("{}.fptas{}.value".format(backpack_size, int(accuracy*100)), end=",")
        print()

        for id_inst, instance in instances.items():
            print(solutions[id_inst].get_cost(), end=",")
            for accuracy in accuracies:
                fptas = copy(instance).fptas(accuracy)
                print(fptas.get_cost(), end=",")
            print()


    # FPTAS speed mode
    if mode == "-fs":

        for accuracy in accuracies:
            print("{}.fptas{}.time".format(backpack_size, int(accuracy*100)), end=",")
        print()

        for id_inst, instance in instances.items():
            for accuracy in accuracies:
                fptas = copy(instance).fptas(accuracy)

        for id_inst, inst in enumerate(measured_time):
            print (inst['time'], end=',')
            if (id_inst + 1)  % len(accuracies) == 0:
                print()



if __name__ == "__main__":
    main(sys.argv)