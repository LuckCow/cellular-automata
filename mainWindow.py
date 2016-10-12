from PyQt4 import Qt
import sys
from lifeforms import Lifeforms
from gameOfLife import GameOfLife

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
        for l in self.gol.zoo.species:
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
        self.gol.zoo.funcList[sender.text()]()

    def setLifeform(self):
        sender = self.sender()
        self.lfBut.setText(sender.text())
        self.gol.zoo.setSpecies(sender.text())
        
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

def main():
    
    app = Qt.QApplication(sys.argv)
    w = mainWindow()
    
    sys.exit(app.exec_())
        
if __name__ == '__main__':
    main()