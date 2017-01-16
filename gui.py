from PyQt4 import Qt, uic
import sys
from lifeforms import Lifeforms
from gameOfLife import GameOfLife

class mainWindow(Qt.QMainWindow):
    """
    Main window contains the main GoL widget and toolbar options
    """
    def __init__(self):
        #TODO: Implement copy and paste
        #TODO: implement saving
        #TODO: implement erase all
        #TODO: implement toolbar functions
        #TODO: change timer scale to better control time frames of interest
        super(mainWindow, self).__init__()
        uic.loadUi('gameOfLife.ui', self)
        self.gol = GameOfLife()
        
        self.timer_button.clicked.connect(self.gol.toggleTimer)
        self.timer_slider.valueChanged.connect(self.gol.changeTimerSpeed)
        self.mouse_mode_tab.currentChanged.connect(self.gol.setMouseMode)
        self.edit_toggle.pressed.connect(self.setEditMode1)
        self.edit_fill.clicked.connect(self.setEditMode2)
        self.edit_erase.clicked.connect(self.setEditMode3)

        
        self.gol.setMouseMode(self.mouse_mode_tab.currentIndex())

        self.lf_cw.pressed.connect(self.gol.zoo.rotateRight)
        self.lf_ccw.pressed.connect(self.gol.zoo.rotateLeft)
        self.lf_horizontal.pressed.connect(self.gol.zoo.flipHorizontal)
        self.lf_vertical.pressed.connect(self.gol.zoo.flipVertical)
        self.lf_selection.addItem('Clipboard')
        self.lf_selection.addItems(sorted(list(self.gol.zoo.species.keys())))
        Qt.QObject.connect(self.lf_selection, Qt.SIGNAL("activated(QString)"),
                               self.gol.zoo.setSpecies)

        self.ct_selection.addItems(['Conway'])
        self.setCellType(0)
        self.name_text.returnPressed.connect(self.editCellName)
        self.new_cell.pressed.connect(self.addCellType)
        
        self.horizontalLayout.insertWidget(0, self.gol)

        #self.gol.setFocusPolicy(Qt.Qt.StrongFocus)
        #self.setCentralWidget(self.gol)
        self.initUI()
        self.show()

    def initUI(self):
        pass

    def addCellType(self):
        sel = len(self.gol.cellSet.types)
        self.gol.addCellType()
        self.gol.setCellType(sel)
        self.setCellType(sel)
        self.ct_selection.insertItem(sel, self.gol.cellSet.types[sel]['name'])
        self.ct_selection.setCurrentIndex(sel)
        
    def setCellType(self, sel):
        pass
        '''
        self.gol.setCellType(sel)
        props = self.gol.cellSet.types[sel].getProperties()
        self.survive_min.setValue(props.surviveRange[0])
        self.survive_min.setRange(0, props.surviveRange[1])
        self.survive_max.setValue(props.surviveRange[1])
        self.survive_max.setRange(props.surviveRange[0], 8)
        self.spawn_min.setValue(props.spawnRange[0])
        self.spawn_min.setRange(1, props.spawnRange[1])
        self.spawn_max.setValue(props.spawnRange[1])
        self.spawn_max.setRange(props.spawnRange[0], 8)
        self.name_text.setText(props.name)

        #TODO: enable editing with spin boxes
        #TODO: add color display and editing
        '''

    def editCellName(self):
        newName = self.name_text.text()
        sel = self.ct_selection.currentIndex()
        self.gol.cellSets[sel].name = newName
        self.ct_selection.setItemText(self.ct_selection.currentIndex(), newName)

    def setEditMode1(self):
        self.gol.editMode = 0
    def setEditMode2(self):
        self.gol.editMode = 1
    def setEditMode3(self):
        self.gol.editMode = 2
    
        
def main():
    app = Qt.QApplication(sys.argv)
    w = mainWindow()
    sys.exit(app.exec_())
        
if __name__ == '__main__':
    main()