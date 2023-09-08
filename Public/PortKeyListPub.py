import os
import sys
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGroupBox
import PKLWindow
import ctypes
from datetime import datetime
import csv

def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)

# Make App Icon to be candle
myappid = 'Ostranna Candle Control'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

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

def load_database():
    with open("artedata.txt", "r") as datafile:
        lines = datafile.readlines()
    for line in lines:
        dline = DataLine()
        # try:
            # dline.timestamp = li

# def check_if_dericol_used(dericol):
#     for line in database:
#         if line[]

def append_and_save(dline: DataLine):
    database.append(dline)
    with open("artedata.txt", "a", newline='') as datafile:
        datafile.write(dline.to_string())

class DiaStart(QMainWindow, PKLWindow.Ui_mainDialog):
    grpbxs = []
    curr_indx = 0

    def restart_and_clear_all(self):
        for wdt in self.grpbxs:
            wdt.hide()
        self.lineEditDericol.setText("Какой он?")
        self.TextEditDestination.setPlainText("Куда же?")
        self.lineEditArtefactID.setText("Какой он?")
        self.rbtnMungo.setChecked(True)
        self.rbtn_destination_clicked()
        self.btnNext.hide()
        self.btnBack.hide()
        self.btnClear.hide()
        self.lineEditName.setText("Джон Роберт Смит")
        self.curr_indx = 0
        self.grpbxs[self.curr_indx].show()

    # ==== Buttons ====
    def btn_start_clicked(self):
        self.btnNext.show()
        self.btnBack.show()
        self.btnClear.show()
        self.btn_next_clicked()

    def btn_next_clicked(self):
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
        # Construct datastring
        line = DataLine()
        line.timestamp = '"' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '"'
        line.name =  '"' + self.lineEditName.text() + '"'
        line.artype = '"PortKey"' if self.rbtnPortKey.isChecked() else '"Anchor"'
        line.dericol = '"' + self.lineEditDericol.text() + '"'
        if self.rbtnPortKey.isChecked():
            if self.rbtnMungo.isChecked():
                line.destination = '"Mungo"'
            elif self.rbtnHogwarts.isChecked():
                line.destination = '"Hogwarts Gate"'
            elif self.rbtnDOMP.isChecked():
                line.destination = '"DOMP"'
            elif self.rbtnMinistry.isChecked():
                line.destination = '"Ministry Door"'
            elif self.rbtnOtherDestination.isChecked():
                line.destination = '"' + self.TextEditDestination.toPlainText() + '"'
        line.artid = '"' + self.lineEditArtefactID.text() + '"'
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


app = QtWidgets.QApplication([])

window = DiaStart()
window.show()

app.exec()
