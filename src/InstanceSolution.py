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
