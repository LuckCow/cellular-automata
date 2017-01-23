from PyQt5 import Qt, uic
import sys
from lifeforms import Lifeforms
from gameOfLife import GameOfLife, Edit

class mainWindow(Qt.QMainWindow):
    """
    Main window contains the main GoL widget and toolbar options
    Ui elements are imported from mainWindow.ui, which was created with Qt designer
    The methods are linked in this mainWindow class because I could not figure out how to import my game of life custom widget into Qt designer with python
    """
    def __init__(self):
        #TODO: implement saving
        #TODO: implement intuitive editing methods
        #TODO: implement toolbar functions
        #TODO: reimpliment name editing
        #TODO: implement color display with cell type (possibly editing too)
        #TODO: implement threading so that ui functionality does not slow down with timer generations
        #TODO: add keybindings
        super(mainWindow, self).__init__()
        uic.loadUi('mainWindow.ui', self)
        self.gol = GameOfLife()
        
        self.timer_button.clicked.connect(self.gol.toggleTimer)
        self.timer_slider.valueChanged.connect(self.gol.changeTimerSpeed)
        self.mouse_mode_tab.currentChanged.connect(self.gol.setMouseMode)

        self.editModes = {'edit_toggle':Edit.toggle, 'edit_fill_in': Edit.fillIn,
                          'edit_fill_over': Edit.fillOver, 'edit_erase_all': Edit.eraseAll,
                          'edit_erase_sel': Edit.eraseSelected}
        for key, val in self.editModes.items():
            exec('self.{}.released.connect(self.setEditMode)'.format(key))

        self.gol.setMouseMode(self.mouse_mode_tab.currentIndex())

        self.lf_cw.pressed.connect(self.gol.zoo.rotateRight)
        self.lf_ccw.pressed.connect(self.gol.zoo.rotateLeft)
        self.lf_horizontal.pressed.connect(self.gol.zoo.flipHorizontal)
        self.lf_vertical.pressed.connect(self.gol.zoo.flipVertical)
        self.lf_selection.addItems(sorted(list(self.gol.zoo.species.keys())))
        self.lf_selection.activated[str].connect(self.gol.zoo.setSpecies)
        self.sel_copy.pressed.connect(self.copy)

        self.types = [0]
        self.setCellType(0)
        self.ct_selection.addItems(['Conway'])
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
            for c in self.gol.zoo.species['Clipboard'].copy():
                if c.cid == sel:
                    self.gol.zoo.species['Clipboard'].remove(c)
        
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
        self.gol.cellSet.types[sel]['name'] = newName
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

    def setEditMode(self):
        for i in self.editModes.keys():
            exec('if self.{}.isChecked(): self.gol.editMode = self.editModes["{}"]'.format(i, i))

    def copy(self):
        self.gol.copySelection()
        self.mouse_mode_tab.setCurrentIndex(2)
        self.lf_selection.setCurrentIndex(1) #TODO: fix this instance of hardcoding :P
        self.gol.zoo.setSpecies('Clipboard')
        
def main():
    app = Qt.QApplication(sys.argv)
    w = mainWindow()
    sys.exit(app.exec_())
        
if __name__ == '__main__':
    main()