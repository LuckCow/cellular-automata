class lifeforms():
    """
    Common lifeforms to place
    """
    
    species = {'glider': frozenset({(-1,-1),(1,0),(-1,0),(0,-1),(-1,1)}),
               'LWSS':frozenset({(0,1),(0,4),(1,0),(2,0),(2,4),(3,0),(3,1),(3,2),(3,3)})}
    directions = {'Up':2, 'Down':4, 'Left':1, 'Right':3}
    def __init__(self):
        pass
        

    def getLifeformSet(self, lf, row, col, rowOffset, colOffset, flipDir):
        translatedSet = set()
        for coordPair in self.species[lf]:
            x = coordPair[1] + col + colOffset
            y = coordPair[0] + row + rowOffset
            translatedSet.add((y,x))
        return self.rotateSet(translatedSet, flipDir)

    def rotateSet(self, transSet, flipDir):
        #if flipDir == self.directions['Left']: Not necissary
            #pass
        if flipDir == self.directions['Up']:
            print('up')
            for c in transSet:
                c = (c[0], c[1]*-1) #flip x
            
        elif flipDir == self.directions['Right']:
            for c in transSet:
                c[1] *= -1 #flip both
                c[0] *= -1
            
        elif flipDir == self.directions['Down']:
            for c in transSet:
                c[0] *= -1  #flip y

        return transSet