from PyQt5 import Qt, uic
import sys
from lifeforms import Lifeforms
from gameOfLife import GameOfLife

class mainWindow(Qt.QMainWindow):
    """
    Main window contains the main GoL widget and toolbar options
    """
    def __init__(self):
        #TODO: implement saving
        #TODO: implement intuitive editing methods
        #TODO: implement toolbar functions
        #TODO: reimpliment name editing
        #TODO: implement color display with cell type (possibly editing too)
        #TODO: implement threading so that ui functionality does not slow down with timer generations
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
        self.lf_selection.addItems(sorted(list(self.gol.zoo.species.keys())))
        self.lf_selection.activated[str].connect(self.gol.zoo.setSpecies)
        self.sel_copy.pressed.connect(self.gol.copySelection)

        self.ct_selection.addItems(['Conway'])
        self.types = [0]
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
        self.show()

    def addCellType(self):
        new_id = self.gol.cellSet.id_count
        self.gol.addCellType()
        self.types.append(new_id)
        self.setCellType(-1)
        self.ct_selection.insertItem(self.types[-1], self.gol.cellSet.types[new_id]['name'])
        self.ct_selection.setCurrentIndex(len(self.types)-1)

    def delCellType(self):
        if len(self.types) > 1:
            sel = self.types[self.ct_selection.currentIndex()]
            self.gol.delCellType(sel)
            self.types.remove(sel)
            self.setCellType(0)
            self.ct_selection.removeItem(self.ct_selection.currentIndex())
            self.ct_selection.setCurrentIndex(0)
        
    def setCellType(self, index):
        sel = self.types[index]
        self.gol.setCellType(sel)
        props = self.gol.cellSet.types[sel]
        for i in range(1, 9):
            exec('self.sp{}.setChecked(i in self.gol.cellSet.types[sel]["spawn"])'.format(i))
            exec('self.sp{}_2.setChecked(i in self.gol.cellSet.types[sel]["survive"])'.format(i))
        self.name_text.setText(props['name'])


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