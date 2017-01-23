from random import paretovariate, randint, choice
from collections import namedtuple, defaultdict, Counter

TypeProperties = namedtuple('TypeProperties', ['color', 'survive', 'spawn'])
Point = namedtuple('Point', ['y', 'x'])

class Cell():
    def __init__(self, y, x, cid):
        self.y, self.x, self.cid = y, x, cid

    def __hash__(self):
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
        if i == 1:
            return self.x
        if i == 2:
            return self.cid

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
            color = randint(0, 2**24)

        #TODO: Add random behavior to defaults
        if not spawn:
            spawn = [3]

        if not survive:
            survive = [2, 3]

        if not name:
            name = choice(self.namePool)
            self.namePool.remove(name)

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

    def reset(self):
        print('TODO: reset')
    


    #TODO: other non Qt related stuff here