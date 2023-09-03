from PyQt6 import QtWidgets
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGroupBox
import PKLWindow


class DiaStart(QMainWindow, PKLWindow.Ui_mainDialog):
    grpbxs = []
    curr_indx = 0

    def restore_defaults(self):
        self.lineEditDericol.setText("Какой он?")
        self.lineEditDestination.setText("Куда же?")
        self.lineEditArtefactID.setText("Какой он?")
        self.rbtnMungo.setChecked(True)

    def restart_and_clear_all(self):
        for wdt in self.grpbxs:
            wdt.hide()
        self.restore_defaults()
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

    # ==== Constructor ====
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(QSize(375, 375))
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
        self.btnComplete.clicked.connect(self.btn_next_clicked)
        self.btnOneMore.clicked.connect(self.btn_one_more_clicked)
        self.btnEnd.clicked.connect(self.btn_clear_clicked)
        # Start the show
        self.restart_and_clear_all()


app = QtWidgets.QApplication([])

window = DiaStart()
window.show()

app.exec()
