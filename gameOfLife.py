"""
Conway's game of life
Author: Nick Collins
Date: 3/16/2016


Python version 3.4.3
PyQt version 4.8.7 - Documentation: http://pyqt.sourceforge.net/Docs/PyQt4/classes.html

Rules

    Any live cell with fewer than two live neighbours dies, as if caused by under-population.
    Any live cell with two or three live neighbours lives on to the next generation.
    Any live cell with more than three live neighbours dies, as if by over-population.
    Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
(from https://en.wikipedia.org/wiki/Conway's_Game_of_Life)

Features:
GUI
Infinite board with generation of both rendered and nonrendered life
Pause/Varying speed of animation
Can edit state in pause and while running
Can place and rotate a small set of known lifeforms
Pan with right mouse button

Display:
Board
Generation Number
Speed of animation

TODO:
Show generation number
Mutations

Known Bugs:


User Feedback:
A bit difficult to pick up on the controls without explanation
--> add labels for buttons and perhaps a help menu with some explanation about the game
Could be a bit clearer about when the mouse is in erase or draw mode

Addressed user feedback
User expected right click to either pan or give a menu. (NOT DO NEXT GENERATION)
-->added right click mouse panning
"""

from PyQt4 import Qt
import sys
from lifeforms import Lifeforms
from enum import IntEnum
import random
from cellset import CellSet

class Mode(IntEnum):
    #Used for arrow key panning
    edit = 0
    select = 1
    place = 2

class Edit(IntEnum):
    toggle = 0
    fill = 1
    erase = 2
        
        
class GameOfLife(Qt.QWidget):
    mouseDrawMode = 0
    mouseEraseMode = 1
    mousePlaceMode = 2
    
    def __init__(self):
        super(GameOfLife, self).__init__()
        self.mouseMode = self.mouseDrawMode
        self.timer = Qt.QBasicTimer()
        self.timerSpeed = 1000
        self.initUI()

        
    def initUI(self):
        self.sq = 30 # starting square size

        #square size relates to zoom
        self.maxSq = 50
        self.minSq = 5

        #The number of squares rendered
        self.renderWidth = self.size().width() // self.sq
        self.renderHeight  = self.size().height() // self.sq

        #offset of render area relative to global coordinate frame
        self.renderY = 0
        self.renderX = 0

        #offset of squares relative to render area
        self.gridOffsetX = 0
        self.gridOffsetY = 0
        self.cellOffsetX = self.sq/2
        self.cellOffsetY = self.sq/2
        
        self.genCount = 0
        self.c = Qt.Qt.darkCyan
        self.c2 = Qt.Qt.cyan
        self.selectionColor = Qt.QColor(223, 145, 0, 100)
        self.selectingColor = Qt.QColor(223, 145, 0, 64)

        self.zoo = Lifeforms()
        self.lifeformOutline = self.zoo.setPoints
        self.defineRenderRegion()

        self.cellSets = [CellSet(None, [3,3] ,[2,3], Qt.Qt.darkCyan) ]
        self.cellSetsSelection = 0

        self.overpopulation = False
        #Significant slow down was observed between 1700 and 2800 population count

        self.setMouseTracking(True)

        self.rightPressed = False
        self.leftPressed = False
        self.selection = (0, 0, 0, 0)
        self.editMode = Edit.toggle
        self.mousePosition = [0, 0]


    def doGeneration(self): #TODO: add cell deletion with global overpopulation
        #TODO: add mutation 
        #Moves the state to next generation
        activeSet = set() #Set of all dead cells that could change (ie neighbors of living cells)
        nextGen = set()
        
        for cell in self.cellSets:
            #First find set of coordinates that could change (adjacent to living cell)
            for i in cell.coords:
                activeSet.update(self.getNeighborSet(i))
            activeSet.difference_update(cell.coords) #Subtract live cells from neighbors
        
            for i in activeSet:
                if cell.spawn_range[0] <= self.countLiveNeighbors(i) <= cell.spawn_range[1]:
                    nextGen.add(i)
                
            for i in cell.coords: #iterate through currently living cells
                neighbours = self.countLiveNeighbors(i)
                if cell.survive_range[0] <= neighbours <= cell.survive_range[1]:
                    if not self.overpopulation or random.random() > 0.05:
                        nextGen.add(i)
            cell.coords = nextGen.copy() #copy nextGen into current set
            activeSet = set()
            nextGen = set()
        self.genCount +=1
        if self.genCount % 25 == 0:
            print('Total Population: {} @ Generation: {}'.format(len(self.getLivingCells()),self.genCount))

    def getNeighborSet(self, coordPoint):
        retSet = set()
        for i in range(-1,2):
            for j in range(-1,2):
                p = (coordPoint[0]+i, coordPoint[1]+j)
                retSet.add(p)
        retSet.remove(coordPoint)
        return retSet

    def getLivingCells(self):
        retSet = set()
        for celltype in self.cellSets:
            retSet.update(celltype.coords)
        return retSet
            
        
    def countLiveNeighbors(self, point):
        coords = self.getLivingCells()
        return len(coords.intersection(self.getNeighborSet(point)))

    def getIndex(self, coords):
        #Coords are (y, x)
        return ((coords[0] + self.sq - self.gridOffsetY) // self.sq,
                (coords[1] + self.sq - self.gridOffsetX) // self.sq) 

    def setMouseMode(self, mode):
        self.mouseMode = mode
        
    def mousePressEvent(self, e):
        row, col = self.getIndex((e.y(),e.x()))
        self.pressRow = row
        self.pressCol = col
        if e.button() == 2: #Right mouse button: for panning
            self.rightPressed = True
            self.lastMouseX = e.x()
            self.lastMouseY = e.y()
        elif e.button() == 1: #Left mouse button: for selecting
            self.leftPressed = True
            self.lastMouseX = e.x()
            self.lastMouseY = e.y()

        
    def mouseReleaseEvent(self, e):
        #print('Mouse Pressed:','Button:',e.button(),'x',e.x(),'y',e.y())
        row, col = self.getIndex((e.y(),e.x()))
        if e.button() == 1:
            if self.mouseMode == Mode.edit:
                if self.editMode == Edit.toggle:
                    self.mouseDraw(row, col, True)
                elif self.editMode == Edit.fill:
                    self.mouseDraw(row, col, False)
                elif self.editMode == Edit.erase:
                    self.mouseErase(row, col)
            elif self.mouseMode == Mode.place:
                self.mousePlace(row, col)
            elif self.mouseMode == Mode.select:
                self.mouseSelect(row, col)
            self.leftPressed = False
        elif e.button() == 2:
            self.rightPressed = False
        else:
            self.doGeneration()
        self.update()

    def mouseMoveEvent(self, e):
        row, col = self.getIndex((e.y(),e.x()))
        self.mousePosition = [row, col]
        self.update()
        if self.rightPressed: #Pan
            dx = e.x() - self.lastMouseX
            dy = e.y() - self.lastMouseY
            self.panSquares(dx, dy)
            self.lastMouseX = e.x()
            self.lastMouseY = e.y()
            
    def mouseDraw(self, row, col, toggle):
        for i in range(min(self.pressRow, row), max(self.pressRow, row)+1):
            for j in range(min(self.pressCol, col), max(self.pressCol, col)+1):
                p = (i+self.renderY,j+self.renderX)
                if p in self.cellSets[self.cellSetsSelection].coords and toggle:
                    self.cellSets[self.cellSetsSelection].coords.remove(p)
                else:
                    self.cellSets[self.cellSetsSelection].coords.add(p)
                        
    def mouseErase(self, row, col):
        for i in range(min(self.pressRow, row), max(self.pressRow, row)+1):
            for j in range(min(self.pressCol, col), max(self.pressCol, col)+1):
                p = (i+self.renderY,j+self.renderX)
                if p in self.cellSets[self.cellSetsSelection].coords:
                    self.cellSets[self.cellSetsSelection].coords.remove(p)

    def mousePlace(self, row, col):
        form = self.zoo.getLifeformSet(row, col, self.renderY, self.renderX)
        self.cellSets[self.cellSetsSelection].coords.update(form)

    def mouseSelect(self, row, col):
        self.selection = (min(self.pressRow, row), max(self.pressRow, row)+1,
                          min(self.pressCol, col), max(self.pressCol, col)+1)
        
    def wheelEvent(self, e):
        if e.delta() > 0:
            self.zoom(True)
        else:
            self.zoom(False)
            

    def keyPressEvent(self, e):
        if e.key() == Qt.Qt.Key_Space:
            self.doGeneration()
            self.update()
        if e.key() in list(Direc):
            self.panBoard(e.key())

    def panSquares(self, dx, dy): #Right click panning
        #sets offset of squares relative to screen given a dx and dy amount
        self.gridOffsetX -= dx
        self.gridOffsetY -= dy
        self.cellOffsetX -= dx
        self.cellOffsetY -= dy

        #Grid offset: moves grid relative to screen
        if self.gridOffsetX > self.sq or self.gridOffsetX < 0:
            #self.renderX += self.gridOffsetX // self.sq
            self.gridOffsetX %= self.sq
        if self.gridOffsetY > self.sq or self.gridOffsetY < 0:
            #self.renderY += self.gridOffsetY // self.sq
            self.gridOffsetY %= self.sq

        #Cell offset: moves cells relative to grid (midpoint offset for smoother panning)
        if self.cellOffsetX > self.sq or self.cellOffsetX < 0:
            self.renderX += self.cellOffsetX // self.sq
            self.cellOffsetX %= self.sq
        if self.cellOffsetY > self.sq or self.cellOffsetY < 0:
            self.renderY += self.cellOffsetY // self.sq
            self.cellOffsetY %= self.sq

        self.defineRenderRegion()
        self.update()
            
    def paintEvent(self, e):
        qp = Qt.QPainter()
        qp.begin(self)
        self.drawBoard(qp)
        self.drawMode(qp)
        qp.end()

    def drawBoard(self, qp):
        ##Draw all rectangles (grid)
        #fill living ones with black
        for cell in self.cellSets:
            for i in range(0, self.renderWidth):
                for j in range(0, self.renderHeight):
                    qp.drawRect(self.renderRects[j][i])
                    if (j+self.renderY, i+self.renderX) in cell.coords:
                        #might be more efficient to iterate over set instead of having this if statement^
                        qp.fillRect(self.renderRects[j][i], Qt.QColor(cell.color))

    def drawMode(self, qp):
        if self.mouseMode == Mode.place:
            form = self.zoo.getLifeformSet(self.mousePosition[0], self.mousePosition[1], 0, 0)
            for point in form:
                if 0 <= point[1] < self.renderWidth and 0 <= point[0] < self.renderHeight:
                    qp.fillRect(self.renderRects[point[0]][point[1]], self.c2)
        elif self.mouseMode == Mode.select:
            if not self.leftPressed:
                for i in range(self.selection[0], self.selection[1]):
                    for j in range(self.selection[2], self.selection[3]):
                        qp.fillRect(self.renderRects[i][j], self.selectionColor)
            else:
                for i in range(min(self.pressRow, self.mousePosition[0]),
                               max(self.pressRow, self.mousePosition[0]) + 1):
                    for j in range(min(self.pressCol, self.mousePosition[1]),
                                   max(self.pressCol, self.mousePosition[1]) + 1):
                        qp.fillRect(self.renderRects[i][j], self.selectingColor)

    def zoom(self, zoomIn):
        #Zoom changes the size of the rendered squares: smaller squares means more are rendered
        if zoomIn and self.sq < self.maxSq:
            self.sq += 1
            self.cellOffsetY += 0.5
            self.cellOffsetX += 0.5
        elif not zoomIn and self.sq > self.minSq:
            self.sq -= 1
            self.cellOffsetY -= 0.5
            self.cellOffsetX -= 0.5
        self.defineRenderRegion()
        self.update()

    def defineRenderRegion(self): 
        self.renderWidth = self.size().width() // self.sq + 1
        self.renderHeight  = self.size().height() // self.sq + 2
        
        self.renderRects = [[False for i in range(0, self.renderWidth)]
                            for j in range(0, self.renderHeight)]
        s = self.sq
        for i in range(0, self.renderWidth):
            for j in range(0, self.renderHeight):
                self.renderRects[j][i] = Qt.QRect((i*s), (j*s), s, s)
                self.renderRects[j][i].translate(self.gridOffsetX - self.sq, self.gridOffsetY - self.sq)
        
    def timerEvent(self, e):
        self.doGeneration()
        self.update()

    def changeTimerSpeed(self, val):
        self.timerSpeed = val
        if self.timer.isActive():
            self.stopTimer()
            self.startTimer()

    def toggleTimer(self):
        if self.timer.isActive():
            self.stopTimer()
        else:
            self.startTimer()
        
    def startTimer(self):
        #timer sends timerEvent every msTic amount of milliseconds
        #timer sends events to GoL widget (which is self)
        self.timer.start(self.timerSpeed, self)

    def stopTimer(self):
        self.timer.stop()
                
    def resizeEvent(self, e):
        self.defineRenderRegion()

    def resetGame(self):
        self.stopTimer()
        self.genCount = 0
        self.coords = set()
        self.update()

    def setCellType(self, sel):
        self.cellSetsSelection = sel

    def addCellType(self):#TODO: add ARGS
        self.cellSets.append(CellSet())