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
        #TODO: reimpliment timer
        #TODO: implement toolbar functions
        #TODO: implement mutations
        super(mainWindow, self).__init__()
        uic.loadUi('gameOfLife.ui', self)
        self.gol = GameOfLife()
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