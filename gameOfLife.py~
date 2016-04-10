"""
Conway's game of life
Author: Nick Collins
Date: 3/16/2016
Time: 1:27pm
Completed initial functionality: 3:30pm (GUI, generation)
Completed full base functionality: 5:30pm (Timer)

Rules

    Any live cell with fewer than two live neighbours dies, as if caused by under-population.
    Any live cell with two or three live neighbours lives on to the next generation.
    Any live cell with more than three live neighbours dies, as if by over-population.
    Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
(from https://en.wikipedia.org/wiki/Conway's_Game_of_Life)

Features:
GUI
small Fixed board or Zoomable
Pause/Varying speed of animation
Can edit state in pause

Display:
Board
Generation Number
Speed of animation

TODO:
Implement larger board with panning/zooming
Implement preset structure / copy pasting structures (lifeforms)
"""

from PyQt4 import Qt
import sys

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
        restart.triggered.connect(self.gol.resetGame)
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
        
        self.toolbar = self.addToolBar('Tooooooooools')
        self.toolbar.addAction(restart)
        self.toolbar.addWidget(sld)
        self.toolbar.addWidget(timerBut)
        
        self.resize(1800,900)
        self.setWindowTitle('Welcome to Conway')
        self.show()

    def changeTimerSpeed(self, val):
        print(val)
        self.timerSpeed = 1000 / (val + 1)

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
        
        
class GameOfLife(Qt.QWidget):
    def __init__(self):
        super(GameOfLife, self).__init__()

        self.initUI()

    def initUI(self):
        self.h = 500
        self.w = 500
        self.sq = 30
        self.renderWidth = self.size().width() // self.sq
        self.renderHeight  = self.size().height() // self.sq
        self.renderY = (self.h - self.renderHeight) // 2
        self.renderX = (self.w - self.renderWidth) // 2
        
        
        self.genCount = 0

        self.board = [[False for i in range(self.w)] for j in range(self.h)]

        self.c = Qt.Qt.darkCyan

        self.defineRenderRegion()

    def doGeneration(self):
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

    def countLiveNeighbors(self, row, col):
        liveCount = 0
        for i in range(row-1, row+2, 1):
            for j in range(col-1, col+2, 1):
                if i >= 0 and j >=0 and i < self.h and j < self.w:
                    if self.board[i][j]:
                        liveCount += 1
        if self.board[row][col]:
            liveCount -= 1
        return liveCount

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
            for i in range(min(self.pressRow, row), max(self.pressRow, row)+1):
                for j in range(min(self.pressCol, col), max(self.pressCol, col)+1):
                    self.board[i+self.renderY][j+self.renderX] = not self.board[i+self.renderY][j+self.renderX]
        else:
            self.doGeneration()
        self.update()

    def wheelEvent(self, e):
        if e.delta() > 0:
            self.zoom(True)
        else:
            self.zoom(False)
            

    def keyPressEvent(self, e):
        if e.key() == Qt.Qt.Key_Space:
            self.doGeneration()
            self.update()
        elif e.key() == Qt.Qt.Key_Up:
            self.renderY -= 1
        elif e.key() == Qt.Qt.Key_Down:
            self.renderY += 1
        elif e.key() == Qt.Qt.Key_Right:
            self.renderX+= 1
        elif e.key() == Qt.Qt.Key_Left:
            self.renderX -= 1
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
                if self.board[j+self.renderY][i+self.renderX]:
                    qp.fillRect(self.renderRects[j][i], self.c)

    def zoom(self, zoomIn):
        #Max square size: 30
        #Min square size: 6
        if zoomIn and self.sq < 30:
            self.sq += 1
        elif not zoomIn and self.sq > 6:
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
        self.board = [[False for i in range(self.w)] for j in range(self.h)]
        self.update()

def main():
    app = Qt.QApplication(sys.argv)
    w = mainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()