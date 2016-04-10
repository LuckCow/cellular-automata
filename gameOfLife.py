"""
Conway's game of life
Author: Nick Collins
Date: 3/16/2016
Time: 1:27pm
Completed initial functionality: 3:30pm (GUI, generation)
Completed full base functionality: 5:30pm (Timer)

4/1/2016
I implimented storing life as a set of coordinates to allow for better scalability.
Only cells adjacent to living cells need to be considered instead of all NxN cells in 2D space

Python version 4.8.4
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

Display:
Board
Generation Number
Speed of animation

TODO:
Implement preset structure / copy pasting structures (lifeforms)
Implement faster panning
Show generation number

Known Bugs:
Timer slider gives weird console error:
(python3:7461): Gtk-CRITICAL **: IA__gtk_widget_get_direction: assertion 'GTK_IS_WIDGET (widget)' failed
   ^does not seem to affect anything

Using Timer sliders takes focus away from grid (arrow keys move timer slider instead of panning)
"""

from PyQt4 import Qt
import sys
from lifeforms import lifeforms

class mainWindow(Qt.QMainWindow):
    """
    Main window contains the main GoL widget and toolbar options
    """
    def __init__(self):
        super(mainWindow, self).__init__()
        self.gol = GameOfLife()
        self.gol.setFocusPolicy(Qt.Qt.StrongFocus)
        self.setCentralWidget(self.gol)
        self.initUI()
        
        
    def initUI(self):
        exitAction = Qt.QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(Qt.qApp.quit)
        self.addAction(exitAction)
        
        #Restart icon and function
        restart = Qt.QAction('Reset', self)
        restart.setShortcut('Ctrl+N')
        restart.triggered.connect(self.resetGame)
        '''
        #Grid layout
        self.gridContainer = Qt.QWidget()
        self.grid = Qt.QGridLayout()
        self.grid.addWidget(self.timer , 0,0)
        self.grid.addWidget(self.mc, 0, 1)
        self.grid.addWidget(self.b, 1, 0, 20, 2)
        self.gridContainer.setLayout(self.grid)
        #self.grid.setRowMinimumHeight(1, 400)
        #self.grid.setColumnMinimumWidth(0, self.size().width())
        self.setCentralWidget(self.gridContainer)
        '''
        sld = Qt.QSlider(Qt.Qt.Horizontal, self)
        sld.valueChanged.connect(self.changeTimerSpeed)

        self.timer = Qt.QBasicTimer()
        self.timerSpeed = 1000
        timerBut = Qt.QPushButton("Start/Stop", self)
        timerBut.clicked.connect(self.toggleTimer)

        modes = {"Draw":self.gol.mouseDrawMode, "Erase":self.gol.mouseEraseMode,
                 "Place":self.gol.mousePlaceMode}
        self.mouseModeButtons = Qt.QButtonGroup()
        self.mouseModeButtons.setExclusive(True)
        for m in modes:
            but = Qt.QPushButton(m, self)
            but.setCheckable(True)
            but.clicked.connect(self.setMouseMode)
            self.mouseModeButtons.addButton(but, modes[m])
        self.mouseModeButtons.button(0).setChecked(True)
        
        self.toolbar = self.addToolBar('Tooooooooools')
        self.toolbar.addAction(restart)
        self.toolbar.addWidget(sld)
        self.toolbar.addWidget(timerBut)
        vWidget = Qt.QWidget()
        vbox = Qt.QVBoxLayout()
        for b in range(3):
            vbox.addWidget(self.mouseModeButtons.button(b))
        vbox.setSpacing(0)
        vWidget.setLayout(vbox)
        self.toolbar.addWidget(vWidget)

        lifeformMenu = Qt.QMenu('Lifeforms')
        for l in self.gol.lf.species:
            act = Qt.QAction(l, lifeformMenu)
            act.triggered.connect(self.setLifeform)
            lifeformMenu.addAction(act)
        self.lfBut = Qt.QPushButton('LifeForm')
        self.lfBut.setMenu(lifeformMenu)
        self.toolbar.addWidget(self.lfBut)

        self.dial = Qt.QDial()
        self.dial.setRange(0,3)
        self.dial.setValue(1)
        self.toolbar.addWidget(self.dial)
        
        self.resize(1800,900)
        self.setWindowTitle('Welcome to Conway')
        self.show()

    def setLifeformDirection(self):
        self.gol.flipDir = self.dial.value()

    def setLifeform(self):
        sender = self.sender()
        self.lfBut.setText(sender.text())
        self.gol.lifeform = sender.text()
        
    def setMouseMode(self):
        self.gol.mouseMode = self.mouseModeButtons.checkedId()

    def changeTimerSpeed(self, val):
        self.timerSpeed = 1000 / (val + 1)
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
        #timer sends events to GoL widget
        self.timer.start(self.timerSpeed, self.gol)

    def stopTimer(self):
        self.timer.stop()

    def resetGame(self):
        self.stopTimer()
        self.gol.resetGame()
        
        
class GameOfLife(Qt.QWidget):
    mouseDrawMode = 0
    mouseEraseMode = 1
    mousePlaceMode = 2

    lf = lifeforms()
    lifeform = 'glider'
    flipDir = 1
    
    def __init__(self):
        super(GameOfLife, self).__init__()
        self.mouseMode = self.mouseDrawMode
        self.initUI()

    def initUI(self):
        self.sq = 30 # starting square size

        #square size relates to zoom
        self.maxSq = 50
        self.minSq = 5

        #The number of squares rendered
        self.renderWidth = self.size().width() // self.sq
        self.renderHeight  = self.size().height() // self.sq

        #board offset of rendering
        self.renderY = 0
        self.renderX = 0
        
        self.genCount = 0
        self.coords = set() #empty set of live cells
        self.c = Qt.Qt.darkCyan

        self.defineRenderRegion()

    def doGeneration(self):
        '''
        #Old generation function (using 2D array)
        #copy current generation
        #Iterate through previous generation, determining state for next. Apply to next
        newGen = [[False for j in range(self.w)] for i in range(self.h)] #init new gen
        for i in range(self.h):
            newGen[i] = self.board[i].copy() #shallow copy current gen
        for i in range(self.h): #rows
            for j in range(self.w): #cols
                neighbours = self.countLiveNeighbors(i, j)
                if self.board[i][j]: #alive
                    if neighbours < 2 or neighbours > 3:
                        newGen[i][j] = False
                    else:
                        newGen[i][j] = True
                else: # dead
                    if neighbours == 3:
                        newGen[i][j] = True
        self.board = newGen #current = new
        self.genCount += 1
        '''
       
        activeSet = set() #Set of all dead cells that could change (ie neighbors of living cells)
        nextGen = set()
        
        for i in self.coords: #Create set of dead cells adjacent to live cells to calculate
            activeSet.update(self.getNeighborSet(i))
        activeSet.difference_update(self.coords) #Subtract live cells from neighbors
        
        for i in activeSet:
            if self.countLiveNeighbors(i) == 3:
                nextGen.add(i)
                
        for i in self.coords: #iterate through currently living cells
            neighbours = self.countLiveNeighbors(i)
            if neighbours >= 2 and neighbours <= 3:
                nextGen.add(i)
        self.coords = nextGen.copy() #copy nextGen into current set
        self.genCount +=1
            

    def getNeighborSet(self, coordPoint):
        retSet = set()
        for i in range(-1,2):
            for j in range(-1,2):
                p = (coordPoint[0]+i, coordPoint[1]+j)
                retSet.add(p)
        retSet.remove(coordPoint)
        return retSet
        
    def countLiveNeighbors(self, point):
        return len(self.coords.intersection(self.getNeighborSet(point)))

    def mousePressEvent(self, e):
        row = (e.y()) // self.sq
        col = (e.x()) // self.sq
        if e.button() == 1:
            self.pressRow = row
            self.pressCol = col

        
    def mouseReleaseEvent(self, e):
        #print('Mouse Pressed:','Button:',e.button(),'x',e.x(),'y',e.y())
        row = (e.y()) // self.sq
        col = (e.x()) // self.sq
        if e.button() == 1:
            if self.mouseMode == self.mouseDrawMode:
                self.mouseDraw(row, col)
            elif self.mouseMode == self.mouseEraseMode:
                self.mouseErase(row, col)
            else:
                self.mousePlace(row, col)
        else:
            self.doGeneration()
        self.update()

    def mouseDraw(self, row, col):
        for i in range(min(self.pressRow, row), max(self.pressRow, row)+1):
            for j in range(min(self.pressCol, col), max(self.pressCol, col)+1):
                p = (i+self.renderY,j+self.renderX)
                if p in self.coords:
                    self.coords.remove(p)
                else:
                    self.coords.add(p)
                        
    def mouseErase(self, row, col):
        for i in range(min(self.pressRow, row), max(self.pressRow, row)+1):
            for j in range(min(self.pressCol, col), max(self.pressCol, col)+1):
                p = (i+self.renderY,j+self.renderX)
                if p in self.coords:
                    self.coords.remove(p)

    def mousePlace(self, row, col):
        form = self.lf.getLifeformSet(self.lifeform, row, col, self.renderY, self.renderX, self.flipDir)
        self.coords.update(form)
        
    def wheelEvent(self, e):
        if e.delta() > 0:
            self.zoom(True)
        else:
            self.zoom(False)
            

    def keyPressEvent(self, e):
        #this is the janky formula I came up with to convert square size to a panning scale
        panScale = int(1/float(self.sq * 0.01)) 
        #print('panScale', panScale)
        if e.key() == Qt.Qt.Key_Space:
            self.doGeneration()
            self.update()
        elif e.key() == Qt.Qt.Key_Up:
            self.renderY -= panScale
        elif e.key() == Qt.Qt.Key_Down:
            self.renderY += panScale
        elif e.key() == Qt.Qt.Key_Right:
            self.renderX += panScale
        elif e.key() == Qt.Qt.Key_Left:
            self.renderX -= panScale
        self.update()
    
    def paintEvent(self, e):
        qp = Qt.QPainter()
        qp.begin(self)
        self.drawBoard(qp)
        qp.end()

    def drawBoard(self, qp):
        ##Draw all rectangles (grid)
        #fill living ones with black
        
        for i in range(0, self.renderWidth):
            for j in range(0, self.renderHeight):
                qp.drawRect(self.renderRects[j][i])
                if (j+self.renderY, i+self.renderX) in self.coords:
                    #might be more efficient to iterate over set instead of having this if statement^
                    qp.fillRect(self.renderRects[j][i], self.c)

    def zoom(self, zoomIn):
        #Zoom changes the size of the rendered squares: smaller squares means more are rendered
        if zoomIn and self.sq < self.maxSq:
            self.sq += 1
        elif not zoomIn and self.sq > self.minSq:
            self.sq -= 1
        self.defineRenderRegion()
        self.update()

    def defineRenderRegion(self):
        self.renderWidth = self.size().width() // self.sq
        self.renderHeight  = self.size().height() // self.sq
        
        self.renderRects = [[False for i in range(0, self.renderWidth)]
                            for j in range(0, self.renderHeight)]
        s = self.sq
        for i in range(0, self.renderWidth):
            for j in range(0, self.renderHeight):
                self.renderRects[j][i] = Qt.QRect((i*s), (j*s), s, s)
        
    def timerEvent(self, e):
        self.doGeneration()
        self.update()
       
                
    def resizeEvent(self, e):
        self.defineRenderRegion()

    def resetGame(self):
        self.genCount = 0
        self.coords = set()
        self.update()

def main():
    
    app = Qt.QApplication(sys.argv)
    w = mainWindow()

    l = lifeforms()
    print(l.species['glider'])
    
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    main()