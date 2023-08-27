from PyQt6 import QtWidgets
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
import PKLStart

class DiaStart(QMainWindow, PKLStart.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(QSize(400, 300))
        self.btnStart.clicked.connect(start_btn_clicked)

def start_btn_clicked():
    print("Strt")


app = QtWidgets.QApplication([])

window = DiaStart()
window.show()

app.exec()