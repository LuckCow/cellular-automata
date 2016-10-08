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

Display:
Board
Generation Number
Speed of animation

TODO:
Implement copy pasting structures (lifeforms)
Show generation number

Known Bugs:
Timer slider gives weird console error:
(python3:7461): Gtk-CRITICAL **: IA__gtk_widget_get_direction: assertion 'GTK_IS_WIDGET (widget)' failed
   ^does not seem to affect anything

User Feedback:
A bit difficult to pick up on the controls without explanation
--> add labels for buttons and perhaps a help menu with some explanation about the game
Could be a bit clearer about when the mouse is in erase or draw mode
User expected right click to either pan or give a menu. (NOT DO NEXT GENERATION)
-->Possibly add right click mouse panning
"""

from PyQt4 import Qt
import sys
from lifeforms import lifeform

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

        #Timer Slider
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
            but.setFocusPolicy(Qt.Qt.NoFocus)
            self.mouseModeButtons.addButton(but, modes[m])
        self.mouseModeButtons.button(0).setChecked(True)
        
        self.toolbar = self.addToolBar('Tooooooooools')
        self.toolbar.addAction(restart)
        sld.setFocusPolicy(Qt.Qt.NoFocus)
        self.toolbar.addWidget(sld)
        timerBut.setFocusPolicy(Qt.Qt.NoFocus)
        self.toolbar.addWidget(timerBut)
        
        vWidget = Qt.QWidget()
        vbox = Qt.QVBoxLayout()
        for b in range(3):
            vbox.addWidget(self.mouseModeButtons.button(b))
        vbox.setSpacing(0)
        vWidget.setLayout(vbox)
        vWidget.setFocusPolicy(Qt.Qt.NoFocus)
        self.toolbar.addWidget(vWidget)

        lifeformMenu = Qt.QMenu('Lifeforms')
        for l in self.gol.species:
            act = Qt.QAction(l, lifeformMenu)
            act.triggered.connect(self.setLifeform)
            lifeformMenu.addAction(act)
        self.lfBut = Qt.QPushButton('LifeForm')
        self.lfBut.setMenu(lifeformMenu)
        self.lfBut.setFocusPolicy(Qt.Qt.NoFocus)
        self.toolbar.addWidget(self.lfBut)

        # I hard coded the transform buttons because
        #python kept messing up the order of them with the dictionary loop
        vWidget = Qt.QWidget()
        vbox = Qt.QVBoxLayout()
        but = Qt.QPushButton('Flip Horizontal', self)
        but.clicked.connect(self.transformLifeform)
        but.setFocusPolicy(Qt.Qt.NoFocus)
        vbox.addWidget(but)
        but = Qt.QPushButton('Flip Vertical', self)
        but.clicked.connect(self.transformLifeform)
        but.setFocusPolicy(Qt.Qt.NoFocus)
        vbox.addWidget(but)
        vbox.setSpacing(0)
        vWidget.setLayout(vbox)
        vWidget.setFocusPolicy(Qt.Qt.NoFocus)
        self.toolbar.addWidget(vWidget)

        vWidget = Qt.QWidget()
        vbox = Qt.QVBoxLayout()
        but = Qt.QPushButton('Rotate Right', self)
        but.clicked.connect(self.transformLifeform)
        but.setFocusPolicy(Qt.Qt.NoFocus)
        vbox.addWidget(but)
        but = Qt.QPushButton('Rotate Left', self)
        but.clicked.connect(self.transformLifeform)
        but.setFocusPolicy(Qt.Qt.NoFocus)
        vbox.addWidget(but)
        vbox.setSpacing(0)
        vWidget.setLayout(vbox)
        vWidget.setFocusPolicy(Qt.Qt.NoFocus)
        self.toolbar.addWidget(vWidget)

        
        self.resize(1800,900)
        self.setWindowTitle('Welcome to Conway')
        self.show()
        
    def transformLifeform(self):
        sender = self.sender()
        self.gol.species[self.gol.lf].funcList[sender.text()]()

    def setLifeform(self):
        sender = self.sender()
        self.lfBut.setText(sender.text())
        self.gol.lf = sender.text()
        
    def setMouseMode(self):
        self.gol.mouseMode = self.mouseModeButtons.checkedId()
        self.gol.update()

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

    lf = 'glider'
    species = {'glider': lifeform({(-1,-1),(1,0),(-1,0),(0,-1),(-1,1)}),
               'LWSS': lifeform({(0,1),(0,4),(1,0),(2,0),(2,4),(3,0),(3,1),(3,2),(3,3)}),
               'toad': lifeform({(0,2),(1,0),(1,3),(2,0),(2,3),(3,1)}),
               'beacon': lifeform({(0,0),(0,1),(1,0),(2,3),(3,2),(3,3)}),
               'pentadecathlon': lifeform({(0,1),(1,1),(2,0),(2,2),(3,1),(4,1),
                                           (5,1),(6,1),(7,2),(7,0),(8,1),(9,1)}),
               'R-pentomino': lifeform({(0,1),(0,2),(1,0),(1,1),(2,1)}),
               'Diehard': lifeform({(0,6),(1,0),(1,1),(2,1),(2,5),(2,6),(2,7)}),
               'Acorn': lifeform({(0,1),(1,3),(2,0),(2,1),(2,4),(2,5),(2,6)}),
               'Infinity Line': lifeform({(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(0,9),(0,10),(0,11),
                                          (0,12),(0,13),(0,17),(0,18),(0,19),(0,26),(0,27),(0,28),(0,29),(0,30),
                                          (0,31),(0,32),(0,34),(0,35),(0,36),(0,37),(0,38)})
               }
    
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
        self.c2 = Qt.Qt.cyan

        self.lifeformOutline = set()

        self.defineRenderRegion()

        self.setMouseTracking(True)

    def doGeneration(self):
        #Moves the state to next generation
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

    def mouseMoveEvent(self, e):
        if self.mouseMode == self.mousePlaceMode:
            row = (e.y()) // self.sq
            col = (e.x()) // self.sq
            self.lifeformOutline = self.species[self.lf].getLifeformSet(row, col, 0, 0)
            self.update()
            #print(self.lifeformOutline)

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
        form = self.species[self.lf].getLifeformSet(row, col, self.renderY, self.renderX)
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

        if self.mouseMode == self.mousePlaceMode:
            for coords in self.lifeformOutline:
                if coords[0] >= 0 and coords[0] < self.renderHeight and coords[1] >= 0 and coords[1] < self.renderWidth:
                    qp.fillRect(self.renderRects[coords[0]][coords[1]], self.c2)

        #Draw mouse placing lifeform outline
            

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
    
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    main()