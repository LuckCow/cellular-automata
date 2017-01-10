from random import normalvariate, randint

class CellSet:
    def __init__(self, init_set=None, sprange=None, srrange=None, color=None):
        self.coords = set()
        self.nextGen = set()
        if init_set:
            self.coords.update(init_set)
        self.gen_count = 0
        
        if not color:
            self.color = randint(0, 2**24)
        else:
            self.color = color
        
        if not sprange:
            self.spawn_range = sorted([round(normalvariate(3,0.5)), round(normalvariate(3,0.5))])
        else:
            self.spawn_range = sprange
        if not srrange:
            self.survive_range = sorted([round(normalvariate(2,1.25)), round(normalvariate(3,1.25))])
        else:
            self.survive_range = srrange
        print("spawn range: {}, survive range: {}".format(self.spawn_range, self.survive_range))

    def update_coords(self):
        self.gen_count += 1
        self.coords = self.nextGen.copy()
        self.nextGen = set()