"""
Cellular Automata Game
Author: Nick Collins
Date: 3/16/2016

This is the game of life board widget
It contains the board drawing, panning, zooming, and editing functionality
"""

from PyQt5 import Qt
import sys
from lifeforms import Lifeforms
from enum import IntEnum
from collections import defaultdict
from cellset import CellSet, Cell

class Mode(IntEnum):
    edit = 0
    select = 1
    place = 2

class Edit(IntEnum):
    toggle = 0
    fillIn = 1
    fillOver = 2
    eraseAll = 3
    eraseSelected = 4
        
        
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
        
        self.selectionColor = Qt.QColor(223, 145, 0, 100)
        self.selectingColor = Qt.QColor(223, 145, 0, 64)

        self.zoo = Lifeforms()
        self.lifeformOutline = self.zoo.setPoints
        self.defineRenderRegion()

        self.cellSet = CellSet()
        self.addCellType('Conway', 20000, [3, 2], [3])
        self.selId = 0

        self.setMouseTracking(True)

        self.rightPressed = False
        self.leftPressed = False
        self.selection = (0, 0, 0, 0)
        self.editMode = Edit.toggle
        self.mousePosition = [0, 0]


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
                    self.mouseToggle(row, col)
                if self.editMode == Edit.fillIn:
                    self.mouseFill(row, col, False)
                elif self.editMode == Edit.fillOver:
                    self.mouseFill(row, col, True)
                elif self.editMode == Edit.eraseAll:
                    self.mouseErase(row, col)
                elif self.editMode == Edit.eraseSelected:
                    self.mouseErase(row, col, self.selId)
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

    def mouseToggle(self, row, col):
        for i in range(min(self.pressRow, row), max(self.pressRow, row)+1):
            for j in range(min(self.pressCol, col), max(self.pressCol, col)+1):
                p = (i+self.renderY,j+self.renderX)
                self.cellSet.toggle_cell(p, self.selId)
            
    def mouseFill(self, row, col, override):
        for i in range(min(self.pressRow, row), max(self.pressRow, row)+1):
            for j in range(min(self.pressCol, col), max(self.pressCol, col)+1):
                p = (i+self.renderY,j+self.renderX)
                self.cellSet.add_cell(p, self.selId, override)
                        
    def mouseErase(self, row, col, cid=None):
        for i in range(min(self.pressRow, row), max(self.pressRow, row)+1):
            for j in range(min(self.pressCol, col), max(self.pressCol, col)+1):
                p = (i+self.renderY,j+self.renderX)
                self.cellSet.remove_cell(p, cid) #Change to only delete selected type

    def mousePlace(self, row, col):
        form = self.zoo.getLifeformSet(row, col, self.renderY, self.renderX, self.selId)
        for cell in form:
            self.cellSet.cells.discard(cell)
            self.cellSet.cells.add(cell)

    def mouseSelect(self, row, col): #TODO: keep selection in same place in space
        self.selection = (min(self.pressRow, row) + self.renderY, max(self.pressRow, row)+1 + self.renderY,
                          min(self.pressCol, col) + self.renderX, max(self.pressCol, col)+1 + self.renderX)

    def copySelection(self):
        sel = set()
        for cell in self.cellSet.cells:
            if self.selection[0] <= cell.y < self.selection[1] \
               and self.selection[2] <= cell.x < self.selection[3]:
                translatedCell = Cell(cell.y - self.selection[0], cell.x - self.selection[2], cell.cid)
                sel.add(translatedCell)
        self.zoo.species['Clipboard'] = sel
        
    def wheelEvent(self, e):
        if e.angleDelta().y() > 0:
            self.zoom(True)
        else:
            self.zoom(False)
            

    def keyPressEvent(self, e):
        if e.key() == Qt.Qt.Key_Space:
            self.cellSet.doGeneration()
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
            self.gridOffsetX %= self.sq
        if self.gridOffsetY > self.sq or self.gridOffsetY < 0:
            self.gridOffsetY %= self.sq

        #Cell offset: moves cells relative to grid (midpoint offset for smoother panning)
        if self.cellOffsetX > self.sq or self.cellOffsetX < 0:
            self.renderX += int(self.cellOffsetX // self.sq)
            self.cellOffsetX %= self.sq
        if self.cellOffsetY > self.sq or self.cellOffsetY < 0:
            self.renderY += int(self.cellOffsetY // self.sq)
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
        #fill living ones with corresponding color
        for i in range(0, self.renderWidth):
            for j in range(0, self.renderHeight):
                qp.drawRect(self.renderRects[j][i])
        for c in self.cellSet.cells:
            relY, relX = int(c.y - self.renderY), int(c.x - self.renderX)
            if 0 <= relY < self.renderHeight and 0 <= relX < self.renderWidth:
                qp.fillRect(self.renderRects[relY][relX],
                            Qt.QColor(self.cellSet.types[c.cid]['color']))

    def drawMode(self, qp):
        #Draw placement or selection indicators according to mouse mode
        if self.mouseMode == Mode.place:
            selColor = Qt.QColor()
            form = self.zoo.getLifeformSet(self.mousePosition[0], self.mousePosition[1], 0, 0, self.selId)
            for point in form:
                selColor.setRgb(self.cellSet.types[point.cid]['color'])
                selColor.setAlpha(155)
                if 0 <= point[1] < self.renderWidth and 0 <= point[0] < self.renderHeight:
                    qp.fillRect(self.renderRects[point[0]][point[1]], selColor)
        elif self.mouseMode == Mode.select:
            if not self.leftPressed:
                y0, y1 = self.selection[0] - self.renderY, self.selection[1] - self.renderY
                x0, x1 = self.selection[2] - self.renderX, self.selection[3] - self.renderX
                for i in range(y0, y1):
                    for j in range(x0, x1):
                        if 0 <= i < self.renderHeight and 0 <= j < self.renderWidth:
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
        self.cellSet.doGeneration()
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
        self.cellSet.reset()
        self.update()

    def setCellType(self, sel):
        self.selId = sel

    def addCellType(self, name=None, color=None, survive=None, spawn=None):
        return self.cellSet.add_new_type(name, color, survive, spawn)

    def delCellType(self, sel):
        self.cellSet.del_type(sel)
