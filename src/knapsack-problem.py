#!/usr/bin/env python3

import sys
from itertools import combinations
from math import floor

import numpy as np
from copy import copy

from InstanceSolution import *
from Instance import *
from utils import *

from Solver import *
import click

def parametrized(instance_file, algorithm):
    instances = {}
    solutions = {}
    relative_errors = []


    for instance_line in instance_file:
        instance = Instance(instance_line.rstrip('\n'))
        instances.update({instance.get_id(): instance})
    
    print("knapsack_id,algorithm,no_items,price,time_ms")


    # backpack_size = next(iter(solutions.values())).get_no_items()
    for id_inst, instance in instances.items():
        if algorithm == "heuristic":
            computed = instance.with_heuristic()
        elif algorithm == "branch_bound":
            method = BranchBound()
            computed = method.solve(instance)
        elif algorithm == "genetic":
            method = Genetic()
            computed = method.solve(instance)
        elif algorithm == "dynamic":
            computed = instance.dynamic()
        elif algorithm == "fptas":
            computed = instance.fptas(75)
        elif algorithm == "brute_force":
            computed = instance.brute_force()
        time = measured_time[-1]['time']
        print(f'{id_inst},{algorithm},{instance.no_items},{computed.get_cost()},{time}')


def genetic(instance_file, xover_probability=0.4, mutation_probability=0.1, elitism_count=10,
            tournament_count=16, tournament_pool_size=2, generations=1000):
    instances = {}

    # print("xover_probability", xover_probability,
    #     "mutation_probability", mutation_probability, 
    #     "elitism_count", elitism_count,
    #     "tournament_count", tournament_count, 
    #     "tournament_pool_size", tournament_pool_size, 
    #     "generations", generations)

    for instance_line in instance_file:
        instance = Instance(instance_line.rstrip('\n'))
        instances.update({instance.get_id(): instance})

    for id_inst, instance in instances.items():

        method = Genetic(xover_probability=xover_probability,
                         mutation_probability=mutation_probability, 
                         elitism_count=elitism_count,
                         tournament_count=tournament_count, 
                         tournament_pool_size=tournament_pool_size, 
                         generations=generations,
                         verbose=True)
        computed = method.solve(instance)
        # print(f'{id_inst},genetic,{instance.no_items},{computed.get_cost()}')
        # print ("ge:", computed)

        method = BranchBound()
        computed = method.solve(instance)
        # print(f'{id_inst},branch,{instance.no_items},{computed.get_cost()}')
        # print ("Bb:", computed)
        # print("-----")


    pass

def print_usage():
    print("Instance and/or solution file not passed as parameter.\n",
       "Usage:", "knapsack.py", "-e/-s <instance_file> <solution_file>\n",
       "    -p <instance_file> [heuristic/dynamic/fptas/branch_bound/brute_force] parametrized mode\n",
       "    -e measures relative error compared to the reference solution\n",
       "    -s measures speed of both brute force and heuristic computations\n",
       "    -fe measures error FPTAS algorithm depending on accurancy\n",
       "    -fs measures speed of FPTAS algorithm depending on accurancy") 

@click.command()
@click.option('-m', '--mode', default="genetic", help='Output mode.   [default: genetic]')
@click.option('-a', '--algorithm', metavar='algorithm', help='Algorithm to chose when running parametrized mode.')
@click.option('-xp', '--xover_probability', default=0.4, type=float, help='xover_probability.')
@click.option('-mp', '--mutation_probability', default=0.1, type=float, help='mutation_probability.')
@click.option('-ec', '--elitism_count', default=10, type=int, help='elitism_count.')
@click.option('-tc', '--tournament_count', default=16, type=int, help='tournament_count.')
@click.option('-tps', '--tournament_pool_size', default=2, type=int, help='tournament_pool_size.')
@click.option('-ge', '--generations', default=1000, help='generations.')
@click.argument('instance_file', nargs=2)
# @click.argument('solution_file', nargs=-1)
def main(mode, algorithm, instance_file, xover_probability, mutation_probability, elitism_count,
            tournament_count, tournament_pool_size, generations):
    if instance_file == None:
        print ("Instance file not supplied!", file=sys.stderr)
        sys.exit(1)


    instance_file_ptr = open(instance_file[1], "r")

    if mode == "parametrized":
        parametrized(instance_file_ptr, algorithm)

    if mode == "genetic":
        genetic(instance_file_ptr, 
                xover_probability=xover_probability,
                mutation_probability=mutation_probability, 
                elitism_count=elitism_count,
                tournament_count=tournament_count, 
                tournament_pool_size=tournament_pool_size, 
                generations=generations)


if __name__ == "__main__":
    main(sys.argv)
