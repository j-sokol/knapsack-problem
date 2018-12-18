from utils import *

from InstanceSolution import InstanceSolution



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


