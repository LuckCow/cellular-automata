"""
Board is implemented using a set of coordinate points with their corresponding cell id.
A dictionary is also stored to map the id to behavior, color, and name. 

Rules
    There are different types of cells known as 'species'.
The behavior of each cell is specified by a set of numbers for spawning and surviving.
Each generation, a cell will remain if the number of neighbors is in its survive set.
Similarly, a new cell will appear in a cell which has the number of neighbors in its spawn set.
Other cell species count toward both requirements.

Reference pages:
https://en.wikipedia.org/wiki/Conway's_Game_of_Life
https://en.wikipedia.org/wiki/Cellular_automaton
"""

import random
from collections import namedtuple, defaultdict, Counter

TypeProperties = namedtuple('TypeProperties', ['color', 'survive', 'spawn'])
Point = namedtuple('Point', ['y', 'x'])

class Cell():
    def __init__(self, y, x, cid):
        self.y, self.x, self.cid = y, x, cid

    def __hash__(self):
        #Only the x and y coordinates are hashed so only one type of cell can occupy a location
        return hash((self.y, self.x))

    def __eq__(self, other):
        if type(other) is type(self):
            if self.x == other.x and self.y == other.y:
                return True
        elif self.x == other[1] and self.y == other[0]:
            return True
        return False

    def __repr__(self):
        return 'Point object:({}, {}), id:{})'.format(self.y, self.x, self.cid)

    def __getitem__(self, i):
        if i == 0:
            return self.y
        elif i == 1:
            return self.x
        elif i == 2:
            return self.cid
        else:
            raise KeyError

class CellSet:
    def __init__(self):
        self.cells = set()
        self.types = {}
        self.namePool = ['Mecklen', 'Raleigh', 'Clemmons', 'Durham', 'Cary', 'Concord', 'Forsyth',
                         'Gastonia', 'Cornelius', 'Garner', 'Boone', 'Apex', 'Wilming', 'Alamance',
                         'Cabarrus', 'Kanna', 'Bern', 'Watuaga', 'Aulan', 'Conetoe', 'Cooleemee']
        self.id_count = 0
        self.gen_count = 0

    def doGeneration(self):
        nextGen = set()
        spawnPossibilities = defaultdict(Counter)
        for c in self.cells:
            num_neighbors = 0
            for i in range(-1,2):
                for j in range(-1,2):
                    if not (i == 0 and j == 0):
                        p = (c.y + i, c.x + j)
                        spawnPossibilities[p][c.cid] += 1
                        if p in self.cells:
                            num_neighbors += 1
            if num_neighbors in self.types[c.cid]['survive']:
                nextGen.add(c)
        for point, id_counter in spawnPossibilities.items():
            num_neighbors = sum(id_counter.values())
            for cellid in id_counter.copy():
                if num_neighbors not in self.types[cellid]['spawn']:
                    del id_counter[cellid]
            if id_counter:
                nextGen.add(Cell(point[0], point[1], id_counter.most_common(1)[0][0]))
        self.cells = nextGen
        self.gen_count += 1
                    

    def add_new_type(self, name=None, color=None, survive=None, spawn=None):
        if not color:
            color = random.randint(0, 2**24)

        #TODO: Add random behavior to defaults
        if not spawn:
            center = int(random.triangular(1, 8, 3))
            extra = None
            if random.random() > 0.7:
                if center < 4:
                    extra = center + 1
                else:
                    extra = center - 1
            spawn = [center]
            if extra:
                spawn.append(extra)

        if not survive:
            center = int(random.triangular(1, 8, 3))
            extra = None
            survive = [center]
            while random.random() > 0.4:
                extra = center + random.randint(-3, 3)
                if extra > 0 and extra <= 8 and (extra not in survive):
                    survive.append(extra)

        if not name:
            if self.namePool:
                name = random.choice(self.namePool)
                self.namePool.remove(name)
            else:
                name = 'Unidentified Species #{}'.format(self.id_count)

        self.types[self.id_count] = {'name': name, 'color': color, 'survive': survive, 'spawn': spawn}
        self.id_count += 1
        return name

    def del_type(self, cid):
        del self.types[cid]
        for c in self.cells.copy():
            if c.cid == cid:
                self.cells.remove(c)

    def update_type(self, cid, name=None, color=None, survive=None, spawn=None):
        if color:
            self.types[cid]['color'] = color

        if name:
            self.types[cid]['name'] = name
        
        if spawn:
            self.types[cid]['spawn'] = spawn

        if survive:
            self.types[cid]['survive'] = survive

    def remove_cell(self, coord, cid=None):
        # Removes all cells in specified set of coordinates
        # Removes only specified cid if given, else it removes all
        if not cid:
            self.cells.discard(coord)
        else:
            for c in self.cells:
                if c.y == coord[0] and c.x == coord[1] and c.cid == cid:
                    self.cells.remove(c)
                    break

    def add_cell(self, point, cid, override=False):
        newPoint = Cell(y=point[0], x=point[1], cid=cid)
        if override:
            self.cells.discard(newPoint)
        self.cells.add(newPoint)

    def toggle_cell(self, point, cid):
        newPoint = Cell(y=point[0], x=point[1], cid=cid)
        if newPoint in self.cells:
            self.cells.discard(newPoint)
        else:
            self.cells.add(newPoint)
