import os
from PyQt6 import QtWidgets
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QDialog, QDialogButtonBox, QVBoxLayout, QMessageBox, QHBoxLayout
import PKLWindow
import ctypes
from datetime import datetime
from MapWidget import MapWidget
from kl_strings import clear_string

# Make App Icon to be candle
myappid = 'PortKeyList'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

database_filename = "artedata.txt"
mapdata_filename = "mapdata.txt"

database = []

class DataLine:
    timestamp = ""
    name = ""
    artype = ""
    dericol = ""
    destination = ""
    artid = ""
    def to_string(self):
        return self.timestamp + ',' + self.name + ',' + self.artype + ',' + self.dericol + ',' + self.destination + ',' + self.artid + "\r\n"
    def from_string(self, line):
        chunks = line.rstrip().split(sep=',')
        if len(chunks) == 6:
            self.timestamp = chunks[0]
            self.name = chunks[1]
            self.artype = chunks[2]
            self.dericol = chunks[3]
            self.destination = chunks[4]
            self.artid = chunks[5]
            return True
        else:
            return False

def load_database():
    database.clear()
    try:
        with open(database_filename, "r") as datafile:
            lines = datafile.readlines()
        for line in lines[1:]:
            dline = DataLine()
            if dline.from_string(line):
                database.append(dline)
    except FileNotFoundError:
        pass

def check_if_such_dericol_exists(dericol):
    for line in database:
        if line.dericol == dericol:
            return True
    return False

def check_if_such_artid_exists(artid):
    for line in database:
        if line.artid == artid:
            return True
    return False

def append_and_save(dline: DataLine):
    database.append(dline)
    # Add column names at the beginning of file
    exists = os.path.exists(database_filename)
    with open(database_filename, "a", newline='') as datafile:
        if not exists:
            datafile.write('"Время создания","Имя автора","Тип артефакта","Код пера дериколя","Место назначения","Код артефакта"\n')
        datafile.write(dline.to_string())

class MapDialog(QDialog):
    # Variables to export
    x, y = None, None
    def on_selection(self, x, y):
        self.lblWhatSelected.setText("Выбрано: x={0}; y={1}".format(x, y))
        self.x = x
        self.y = y

    def on_settings_change(self, checked):
        self.maplbl.on_map_settings_change(self.cbShowGrid.isChecked(), self.cbShowDesctrip.isChecked())

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Карта Хогвартса и окрестностей")
        # Buttons
        qbtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(qbtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        # Map
        self.maplbl = MapWidget(mapdata_filename)
        self.maplbl.mapclicked.connect(self.on_selection)
        # Settings
        self.cbShowGrid = QtWidgets.QCheckBox()
        self.cbShowGrid.setText("Координатная сетка")
        self.cbShowGrid.setChecked(True)
        self.cbShowGrid.clicked.connect(self.on_settings_change)
        self.cbShowDesctrip = QtWidgets.QCheckBox()
        self.cbShowDesctrip.setText("Что где")
        self.cbShowDesctrip.setChecked(True)
        self.cbShowDesctrip.clicked.connect(self.on_settings_change)
        # Selection
        self.lblWhatSelected = QtWidgets.QLabel()
        # Construct bottom layout
        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.addWidget(self.cbShowGrid)
        self.bottom_layout.addWidget(self.cbShowDesctrip)
        self.bottom_layout.addWidget(self.lblWhatSelected)
        self.bottom_layout.addWidget(self.buttonBox)
        # Construct main layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.maplbl)
        self.layout.addLayout(self.bottom_layout)
        self.setLayout(self.layout)

class DiaStart(QMainWindow, PKLWindow.Ui_mainDialog):
    grpbxs = []
    curr_indx = 0

    def restart_and_clear_all(self):
        for wdt in self.grpbxs:
            wdt.hide()
        self.lineEditDericol.clear()
        self.TextEditDestination.clear()
        self.lineEditArtefactID.clear()
        self.rbtnMungo.setChecked(True)
        self.rbtn_destination_clicked()
        self.btnNext.hide()
        self.btnBack.hide()
        self.btnClear.hide()
        self.lineEditName.clear()
        self.curr_indx = 0
        self.grpbxs[self.curr_indx].show()

    # ==== Buttons ====
    def btn_start_clicked(self):
        self.btnNext.show()
        self.btnBack.show()
        self.btnClear.show()
        self.btn_next_clicked()

    def btn_next_clicked(self):
        # Check if correct data entered
        if self.grpbxs[self.curr_indx] == self.groupBoxName:
            txt = clear_string(self.lineEditName.text())
            if txt == "":
                QMessageBox.warning(self, "Проблема с именем", "У автора должно быть имя.\nВведите имя автора артефакта.")
                return

        elif self.grpbxs[self.curr_indx] == self.groupBoxQuesse:
            txt = clear_string(self.lineEditDericol.text())
            if txt == "":
                QMessageBox.warning(self, "Проблема с пером", "У пера дериколя должен быть код.\nВведите код пера.")
                return
            txt = '"' + txt + '"'
            if check_if_such_dericol_exists(txt):
                QMessageBox.warning(self, "Проблема с пером", "Такое перо дериколя уже зарегистрировано.\nВведите код другого пера.")
                return

        elif self.grpbxs[self.curr_indx] == self.groupBoxDestination and self.rbtnOtherDestination.isChecked():
            txt = clear_string(self.TextEditDestination.toPlainText())
            if txt == "":
                QMessageBox.warning(self, "Проблема с местом назначения", "Описание места назначения не может быть пустым.\n"
                                                                          "Введите описание места назначения.")
                return

        # Proceed
        self.grpbxs[self.curr_indx].hide()
        # Check if show Destination
        self.curr_indx += 2 if self.grpbxs[self.curr_indx] == self.groupBoxQuesse and self.rbtnAnchor.isChecked() else 1
        self.grpbxs[self.curr_indx].show()
        self.btnNext.setEnabled(self.curr_indx < len(self.grpbxs) - 2) # Disable NEXT btn at last item
        self.btnBack.setEnabled(self.curr_indx > 1 and self.curr_indx != len(self.grpbxs) - 1)

    def btn_back_clicked(self):
        self.grpbxs[self.curr_indx].hide()
        # Check if show Destination
        self.curr_indx -= 2 if self.grpbxs[self.curr_indx] == self.groupBoxArtefact and self.rbtnAnchor.isChecked() else 1
        self.grpbxs[self.curr_indx].show()
        self.btnNext.setEnabled(True)
        self.btnBack.setEnabled(self.curr_indx > 1)

    def btn_clear_clicked(self):
        self.restart_and_clear_all()

    def btn_one_more_clicked(self):
        self.grpbxs[self.curr_indx].hide()
        self.curr_indx = 0
        self.btn_next_clicked()

    def btn_complete_clicked(self):
        txt = clear_string(self.lineEditArtefactID.text())
        if txt == "":
            QMessageBox.warning(self, "Проблема с артефактом", "У артефакта должен быть код .\nВведите код артефакта.")
            return
        line = DataLine()
        # Check if such artid exists
        line.artid = '"' + txt + '"'
        if check_if_such_artid_exists(line.artid):
            QMessageBox.warning(self, "Проблема с артефактом",
                                "Артефакт с таким идентификатором уже зарегистрирован.\n"
                                "Введите другой идентификатор - возможно, нужно взять из коробки новый.")
            return
        # Add other fields
        line.timestamp = '"' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '"'
        line.name =  '"' + clear_string(self.lineEditName.text()) + '"'
        line.artype = '"PortKey"' if self.rbtnPortKey.isChecked() else '"Anchor"'
        line.dericol = '"' + clear_string(self.lineEditDericol.text()) + '"'
        if self.rbtnPortKey.isChecked():
            if self.rbtnMungo.isChecked():
                line.destination = '"Ко входу в Мунго"'
            elif self.rbtnHogwarts.isChecked():
                line.destination = '"К воротам Хогвартса"'
            elif self.rbtnDOMP.isChecked():
                line.destination = '"Ко входу в ДОМП"'
            elif self.rbtnMinistry.isChecked():
                line.destination = '"Ко входу в Министерство"'
            elif self.rbtnOtherDestination.isChecked():
                line.destination = '"' + clear_string(self.TextEditDestination.toPlainText()) + '"'
        append_and_save(line)
        self.btn_next_clicked()

    def rbtn_destination_clicked(self):
        if self.rbtnOtherDestination.isChecked():
            self.lblDestDescription.show()
            self.btnShowMap.show()
            self.TextEditDestination.show()
        else:
            self.lblDestDescription.hide()
            self.btnShowMap.hide()
            self.TextEditDestination.hide()

    def btn_showmap_clicked(self):
        dlg = MapDialog(parent=self)
        if dlg.exec():
            txt = self.TextEditDestination.toPlainText()
            if len(txt) != 0:
                txt += ' '
            self.TextEditDestination.setPlainText(txt + "Карта: x={0}; y={1}".format(dlg.x, dlg.y))

    # ==== Constructor ====
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(QSize(518, 360))
        # Setup sequence
        self.grpbxs.extend([self.groupBoxStart, self.groupBoxName, self.groupBoxType, self.groupBoxQuesse,
                            self.groupBoxDestination, self.groupBoxArtefact, self.groupBoxWhatNext])
        # Set sizes
        rect = self.groupBoxStart.geometry()
        for grpb in self.grpbxs:
            grpb.setGeometry(rect)
        # Setup btns
        self.btnStart.clicked.connect(self.btn_start_clicked)
        self.btnClear.clicked.connect(self.btn_clear_clicked)
        self.btnNext.clicked.connect(self.btn_next_clicked)
        self.btnBack.clicked.connect(self.btn_back_clicked)
        self.btnShowMap.clicked.connect(self.btn_showmap_clicked)
        self.btnComplete.clicked.connect(self.btn_complete_clicked)
        self.btnOneMore.clicked.connect(self.btn_one_more_clicked)
        self.btnEnd.clicked.connect(self.btn_clear_clicked)
        # rbtns of destination
        self.rbtnMinistry.clicked.connect(self.rbtn_destination_clicked)
        self.rbtnDOMP.clicked.connect(self.rbtn_destination_clicked)
        self.rbtnHogwarts.clicked.connect(self.rbtn_destination_clicked)
        self.rbtnMungo.clicked.connect(self.rbtn_destination_clicked)
        self.rbtnOtherDestination.clicked.connect(self.rbtn_destination_clicked)
        # Start the show
        self.restart_and_clear_all()

load_database()

app = QtWidgets.QApplication([])

window = DiaStart()
window.show()

app.exec()
