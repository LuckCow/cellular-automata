from PyQt4 import Qt, uic
import sys
from lifeforms import Lifeforms
from gameOfLife import GameOfLife

class mainWindow(Qt.QMainWindow):
    """
    Main window contains the main GoL widget and toolbar options
    """
    def __init__(self):
        #TODO: implement toolbar functions
        #TODO: implement mutations
        #TODO: change timer scale to better control time frames of interest
        super(mainWindow, self).__init__()
        uic.loadUi('gameOfLife.ui', self)
        self.gol = GameOfLife()

        self.timer_button.clicked.connect(self.gol.toggleTimer)
        self.timer_slider.valueChanged.connect(self.gol.changeTimerSpeed)
        self.mouse_mode_tab.currentChanged.connect(self.gol.setMouseMode)
        self.gol.setMouseMode(self.mouse_mode_tab.currentIndex())
        self.lf_selection.addItem('Clipboard')
        self.lf_selection.addItems(sorted(list(self.gol.zoo.species.keys())))
        Qt.QObject.connect(self.lf_selection, Qt.SIGNAL("activated(QString)"),
                               self.gol.zoo.setSpecies)

        self.ct_selection.addItems(['1', 'New..'])
        
        
        
        self.horizontalLayout.insertWidget(0, self.gol)
        #TODO: put widget in qt designer and have it inherit from both designer and python code
        
        #self.gol.setFocusPolicy(Qt.Qt.StrongFocus)
        #self.setCentralWidget(self.gol)
        self.initUI()
        self.show()

    def initUI(self):
        pass

    def setCellType(self, sel):
        print(sel)
        if sel == len(self.gol.cellSets):
            self.gol.addCellType()
            self.ct_selection.insertItem(len(self.gol.cellSets)-1, str(sel+1)+'.')
        self.gol.setCellType(sel)

def main():
    app = Qt.QApplication(sys.argv)
    w = mainWindow()
    
    sys.exit(app.exec_())
        
if __name__ == '__main__':
    main()