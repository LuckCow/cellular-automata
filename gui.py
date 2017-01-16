from PyQt5 import Qt, uic
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
        self.lf_selection.activated[str].connect(self.gol.zoo.setSpecies)
        self.sel_copy.pressed.connect(self.gol.copySelection)

        self.ct_selection.addItems(['Conway'])
        self.setCellType(0)
        self.name_text.returnPressed.connect(self.editCellName)
        self.new_cell.pressed.connect(self.addCellType)
        self.del_cell.pressed.connect(self.delCellType)

        for i in range(1, 9):
            exec('self.sp{}.clicked.connect(self.editCellProperties)'.format(i, i))
            exec('self.sp{}_2.clicked.connect(self.editCellProperties)'.format(i, i))


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
        self.setCellType(sel)
        self.ct_selection.insertItem(sel, self.gol.cellSet.types[sel]['name'])
        self.ct_selection.setCurrentIndex(sel)

    def delCellType(self): #TODO: figure out indexing when a type is deleted
        sel = self.ct_selection.currentIndex()
        self.gol.delCellType(sel)
        self.setCellType(0)
        self.ct_selection.removeItem(sel)
        self.ct_selection.setCurrentIndex(0)
        
    def setCellType(self, sel):
        self.gol.setCellType(sel)
        props = self.gol.cellSet.types[sel]
        for i in range(1, 9):
            exec('self.sp{}.setChecked(i in self.gol.cellSet.types[sel]["spawn"])'.format(i))
            exec('self.sp{}_2.setChecked(i in self.gol.cellSet.types[sel]["survive"])'.format(i))
        self.name_text.setText(props['name'])

        #TODO: enable editing with spin boxes
        #TODO: add color display and editing

    def editCellName(self):
        newName = self.name_text.text()
        sel = self.ct_selection.currentIndex()
        self.gol.cellSets[sel].name = newName
        self.ct_selection.setItemText(self.ct_selection.currentIndex(), newName)

    def editCellProperties(self):
        sel = self.ct_selection.currentIndex()
        sp = []
        for i in range(1, 9):
            exec('if self.sp{}.isChecked(): sp.append({})'.format(i, i))
        self.gol.cellSet.types[sel]['spawn'] = sp

        sr = []
        for i in range(1, 9):
            exec('if self.sp{}_2.isChecked(): sr.append({})'.format(i, i))
        self.gol.cellSet.types[sel]['survive'] = sr
        print(sr)


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