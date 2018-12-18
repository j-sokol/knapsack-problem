from InstanceSolution import InstanceSolution
from utils import *
import random
import copy

class Solver(object):
    """Generic solver class"""
    def __init__(self):
        super(Solver, self).__init__()

    def solve(self):
        pass
        



class Genetic(Solver):
    """Solver class for Generic algorithm"""
    def __init__(self, xover_probability=0.4, mutation_probability=0.1, elitism_count=10,
                tournament_count=16, tournament_pool_size=2, generations=1000, verbose=False):
        super(Genetic, self).__init__()
        self.population_size = 100
        self.items = []
        self.capacity = 0

        self.xover_probability = xover_probability
        self.mutation_probability = mutation_probability
        self.elitism_count = elitism_count
        self.tournament_count = tournament_count
        self.tournament_pool_size = tournament_pool_size
        self.generations = generations
        self.verbose = verbose

    def save_best(self, best):
        for index, item in enumerate(best):
            if item == True:
                self.items[index]['entered'] = True

    def get_cost(self):
        return sum([x['price'] for x in self.items if x['entered']])
        

    def knap_to_bits(self, items):
        prices = [i['price'] for i in items]
        weights = [i['weight'] for i in items]
        return prices, weights
        
    def fitness_fn(self, population):
        price = 0
        weight = 0

        for index, item in enumerate(population):
            if item == True:
                price = price + self.items[index]['price']
                weight = weight + self.items[index]['weight']
        if weight <= self.capacity:
            return price
        else:
            return 0

    def constraint_fn(self, population):
        weight = 0
        for index, item in enumerate(population):
            if item == True:
                weight = weight + self.items[index]['weight']

        return weight <= self.capacity

    def create_individual(self, indiv_size):
        individual = [ random.choice([1, 0]) for i in range(0, indiv_size)]
        return individual

    def random_individual(self, population):
        pop_range = len(population)
        return population[random.randint(0, pop_range-1)]

    def create_population(self, population_size, indiv_size):
        population = [self.create_individual(indiv_size) for i in range(0, population_size)]
        return population

    def sort_population(self, population):
        """ Sort population acording to fitness function """
        sorted_pop = sorted(population, key=lambda x: self.fitness_fn(x), reverse=True)
        return sorted_pop

    def tournament(self, population, tournament_count, tournament_pool_size):

        new_population = []
        population_size = len(population)

        # Number of tournaments
        for _ in range(tournament_count):
            pool = []

            # Select individuals of tournament
            for _ in range(tournament_pool_size):
                pool.append(self.random_individual(population))
                
            sorted_pop = self.sort_population(pool)

            # Select the best from the tournament
            new_population.append(self.sort_population(pool)[0])
            
        return new_population
        
    def crossover_single(self, in1, in2):
        size = len(in1)
        child = copy.deepcopy(in1)
        midpoint = random.randint(0, size)

        for i in range(0, size):
            if i < midpoint:
                child[i] = in1[i]
            else:
                child[i] = in2[i]
        return child


    def mutator_random_inverse(self, child, mutation_probability):
        for index, item in enumerate(child):
            if odds_are(mutation_probability):
                if item == True:
                    child[index] = 0
                else:
                    child[index] = 1
        return child

    def simulate(self, size):

        # Create initial population
        population = self.create_population(self.population_size, size)

        if self.verbose:
            print("generation,best_combination")
            best = 0

        # Run n generations
        for generation in range(0, self.generations):
            sorted_population = self.sort_population(population)

            new_best = self.fitness_fn(sorted_population[0])

            if self.verbose:
                # if new_best > best:
                #     print(generation, new_best, sep=",")
                #     best = new_best
                print(generation, new_best, sep=",")


            # Selection
            new_population = self.tournament(population, self.tournament_count, self.tournament_pool_size )


            # Elitsm
            del sorted_population[self.elitism_count:]


            new_population.extend(sorted_population)
            sorted_population = self.sort_population(new_population)


            # Fill population with new children
            while len(new_population) != self.population_size:
                child = []
                # Crossover
                if odds_are(self.xover_probability):

                    in1 = self.random_individual(new_population)
                    in2 = self.random_individual(new_population)

                    child = self.crossover_single(in1, in2)

                else:
                    # Just pick random individual
                    child = copy.deepcopy(self.random_individual(population))

                # Mutation
                child = self.mutator_random_inverse(child, self.mutation_probability)

                # Check if mutated/crossed individual is valid
                if self.constraint_fn(child):
                    new_population.append(child)

            population = new_population

        sorted_population = self.sort_population(population)

        return sorted_population[0]

    def solve(self, instance):
        prices, weights = self.knap_to_bits(instance.items)
        self.items = instance.items
        self.capacity = instance.capacity
        


        best = self.simulate(len(prices));

        self.save_best(best)
        return InstanceSolution(no_items=len(self.items), best_cost=self.get_cost(), best_combination=best)




class BranchBound(Solver):
    """Branch and Bound solver class"""
    def __init__(self):
        super(BranchBound, self).__init__()

    @timing
    def solve(self, instance):

        selected_price = 0
        selected_items = []

        # Create list of remaining prices
        remaining_prices = [0] * instance.no_items
        remaining_prices[instance.no_items-1] = instance.items[instance.no_items-1]['price']

        for i in range(instance.no_items-1-1, 0, -1):
            remaining_prices[i] = remaining_prices[i+1] + instance.items[i]['price']

        instance.solve_branch_bound([], 0, 0, remaining_prices)

        # Append zeros to the output
        while len(instance.selected_items) < instance.no_items:
            instance.selected_items.append(0)

        return InstanceSolution(no_items=instance.no_items, best_cost=instance.selected_price, best_combination=instance.selected_items)


        