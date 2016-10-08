class lifeform():
    """
    Common lifeforms to place
    """
    
    def __init__(self, sp):
        self.setPoints = sp
        self.funcList = {'Flip Horizontal': self.flipHorizontal, 'Flip Vertical': self.flipVertical,
                         'Rotate Right': self.rotateRight, 'Rotate Left': self.rotateLeft}
        
    def rotateLeft(self):
        newSet = set()
        for p in self.setPoints:
            newP = (p[1], p[0])
            newSet.add(newP)
        self.setPoints = newSet.copy()
        self.flipVertical()

    def rotateRight(self):
        self.flipVertical()
        newSet = set()
        for p in self.setPoints:
            newSet.add((p[1], p[0]))
        self.setPoints = newSet.copy()

    def flipHorizontal(self):
        newSet = set()
        for p in self.setPoints:
            newSet.add((p[0], p[1]*-1))
        self.setPoints = newSet.copy()

    def flipVertical(self):
        newSet = set()
        for p in self.setPoints:
            newSet.add((p[0]*-1, p[1]))
        self.setPoints = newSet.copy()
            
        
    def getLifeformSet(self, row, col, rowOffset, colOffset):
        translatedSet = set()
        for coordPair in self.setPoints:
            x = coordPair[1] + col + colOffset
            y = coordPair[0] + row + rowOffset
            translatedSet.add((y,x))
        return translatedSet
