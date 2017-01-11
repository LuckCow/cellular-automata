from random import normalvariate, randint, choice
from collections import namedtuple

class CellSet:
    def __init__(self, init_set=None, sprange=None, srrange=None, color=None, name=None):
        self.namePool = ['Charlotte', 'Raleigh', 'Greenboro', 'Durham', 'Cary', 'Concord',
                         'Gastonia', 'Cornelius', 'Carrboro', 'Boone']
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

        if not name:
            self.name = choice(self.namePool)
            self.namePool.remove(self.name)
        else:
            self.name = name

    def update_coords(self):
        self.gen_count += 1
        self.coords = self.nextGen.copy()
        self.nextGen = set()

    def getProperties(self):
        Props = namedtuple('Props', ['surviveRange', 'spawnRange', 'color', 'name']) 
        return Props(surviveRange=tuple(self.survive_range), spawnRange=tuple(self.spawn_range),
                     color=self.color, name=self.name)