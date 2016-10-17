from PyQt4 import Qt, uic
import sys
from lifeforms import Lifeforms
from gameOfLife import GameOfLife

class mainWindow(Qt.QMainWindow):
    """
    Main window contains the main GoL widget and toolbar options
    """
    def __init__(self):
        #TODO: reimpliment mouse editing modes
        #TODO: implement toolbar functions
        #TODO: implement mutations
        #TODO: change timer scale to better control time frames of interest
        super(mainWindow, self).__init__()
        uic.loadUi('gameOfLife.ui', self)
        self.gol = GameOfLife()

        self.timer_button.clicked.connect(self.gol.toggleTimer)
        self.timer_slider.valueChanged.connect(self.gol.changeTimerSpeed)
        
        self.horizontalLayout.insertWidget(0, self.gol)
        #TODO: put widget in qt designer and have it inherit from both designer and python code
        
        #self.gol.setFocusPolicy(Qt.Qt.StrongFocus)
        #self.setCentralWidget(self.gol)
        self.initUI()
        self.show()

    def slot1(self, arg):
        print(arg)

    def initUI(self):
        pass

def main():
    app = Qt.QApplication(sys.argv)
    w = mainWindow()
    
    sys.exit(app.exec_())
        
if __name__ == '__main__':
    main()