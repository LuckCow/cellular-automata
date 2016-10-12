from random import normalvariate

class CellSet:
    def __init__(self, init_set=None, sprange=None, srrange=None):
        self.coords = set().update(init_set)
        self.gen_count = 0
        
        if not sprange:
            self.spawn_range = sorted([normalvariate(3,0.5), normalvariate(3,0.5)])
        if not srrange:
            self.survive_range = sorted([normalvariate(2,1), normalvariate(3,1)])
        print("spawn range: {}, survive range: {}".format(self.spawn_range, self.survive_range))

    def update_coords(self, new_set):
        self.gen_count += 1
        self.coords = new_set