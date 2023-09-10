import os
import sys
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import QSize, Qt, QLineF, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGroupBox, QDialog, QDialogButtonBox, QVBoxLayout, \
    QLabel, QMessageBox, QGraphicsView, QGraphicsScene, QGraphicsLineItem, QStackedLayout, QHBoxLayout
import PKLWindow
import ctypes
from datetime import datetime

# Make App Icon to be candle
myappid = 'Ostranna Candle Control'
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

Descr = []

def descr_append_and_save(x, y, txt):
    Descr.append([x, y, txt])
    with open(mapdata_filename, "a") as datafile:
        datafile.write('"{0}","{1}","{2}"\n'.format(x, y, txt))

def clear_string(s):
    while s[0] in ('"', ' ', '\r', '\n'):
        s = s[1:]
    while s[-1] in ('"', ' ', '\r', '\n'):
        s = s[:-1]
    return s
def load_map_descr():
    Descr.clear()
    try:
        with open(mapdata_filename, "r") as datafile:
            lines = datafile.readlines()
        for line in lines:
            chunks = line.split(sep=',')
            if len(chunks) != 3:
                continue
            x = int(clear_string(chunks[0]))
            y = int(clear_string(chunks[1]))
            txt = clear_string(chunks[2])
            Descr.append([x, y, txt])
    except FileNotFoundError:
        pass

class DescDialog(QDialog):
    def __init__(self, x, y, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Введите описание")
        self.lblCoords = QtWidgets.QLabel()
        self.lblCoords.setText("x={0}; y={1}".format(x, y))
        self.lineeditDescr = QtWidgets.QLineEdit()
        # Buttons
        qbtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(qbtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        # Construct main layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.lblCoords)
        self.layout.addWidget(self.lineeditDescr)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

class MapCanvas(QtWidgets.QLabel):
    # Constants
    coord_step = 20
    font_sz_pix = 14

    # Signals
    mapclicked = pyqtSignal(int, int)
    def __init__(self):
        super().__init__()
        self.clean_pix = QtGui.QPixmap(".\\img/map.png")
        self.coords_pix = QtGui.QPixmap(".\\img/map.png")
        self.descr_pix = QtGui.QPixmap(".\\img/map.png")
        self.coords_descr_pix = QtGui.QPixmap(".\\img/map.png")
        self.must_show_coords = True
        self.must_show_descrip = True
        self.map_x = None
        self.map_y = None
        # Show map primitives
        self.draw_coords(self.coords_pix)
        self.draw_coords(self.coords_descr_pix)
        self.draw_descr(self.descr_pix)
        self.draw_descr(self.coords_descr_pix)
        # Show what needed
        self.redraw_needed_map()

    def get_backgnd_pen(self):
        pen = QtGui.QPen()
        pen.setWidth(1)
        pen.setStyle(Qt.PenStyle.DotLine)
        pen.setColor(Qt.GlobalColor.darkGray)
        return pen

    def get_foregnd_pen(self):
        pen = QtGui.QPen()
        pen.setWidth(1)
        pen.setStyle(Qt.PenStyle.SolidLine)
        pen.setColor(Qt.GlobalColor.red)
        return pen

    def prepare_descr_font(self, painter):
        font = QtGui.QFont()
        font.setFamily("Comic Sans MS")
        font.setPixelSize(self.font_sz_pix)
        painter.setFont(font)
        pen = QtGui.QPen()
        pen.setWidth(1)
        pen.setColor(Qt.GlobalColor.white)
        painter.setPen(pen)

    def draw_coords(self, apixmap):
        xmax = apixmap.width()
        ymax = apixmap.height()
        painter = QtGui.QPainter(apixmap)
        # Lines
        painter.setPen(self.get_backgnd_pen())
        for x in range(0, xmax, self.coord_step):
            painter.drawLine(x, 0, x, ymax)
        for y in range(0, ymax, self.coord_step):
            painter.drawLine(0, y, xmax, y)
        # Letters
        font = QtGui.QFont()
        font.setFamily("Comic Sans MS")
        font.setPixelSize(self.font_sz_pix)
        painter.setFont(font)
        pen = QtGui.QPen()
        pen.setWidth(1)
        pen.setColor(Qt.GlobalColor.white)
        painter.setPen(pen)
        xmap = 1
        ybottom = (ymax // self.coord_step) * self.coord_step - 4
        for x in range(self.coord_step, xmax, self.coord_step):
            if xmax - x < self.coord_step:
                break
            offset = (self.coord_step // 2) - 4 if xmap <= 9 else 1
            painter.drawText(x + offset, ybottom, str(xmap))
            xmap += 1
        ymap = 1
        for y in range(self.coord_step - 4, ymax, self.coord_step):
            if y >= ybottom:
                break
            offset = (self.coord_step // 2) - 4 if ymap <= 9 else 4
            painter.drawText(offset, y, str(ymap))
            ymap += 1
        painter.end()

    def draw_descr(self, apixmap):
        painter = QtGui.QPainter(apixmap)
        self.prepare_descr_font(painter) # Setup font
        for d in Descr:
            painter.drawText(d[0], d[1], d[2])
        painter.end()

    def redraw_needed_map(self):
        if self.must_show_coords and self.must_show_descrip:
            self.setPixmap(self.coords_descr_pix)
        elif self.must_show_coords:
            self.setPixmap(self.coords_pix)
        elif self.must_show_descrip:
            self.setPixmap(self.descr_pix)
        else:
            self.setPixmap(self.clean_pix)
    def on_map_settings_change(self, show_coords, show_descrip):
        self.must_show_coords = show_coords
        self.must_show_descrip = show_descrip
        self.redraw_needed_map()

    def on_rightbtn_click(self, x, y):
        dlg = DescDialog(x, y, parent=self)
        if dlg.exec():
            txt = dlg.lineeditDescr.text()
            descr_append_and_save(x, y, txt)
            # Draw on descr and coords_descr
            painter = QtGui.QPainter(self.descr_pix)
            self.prepare_descr_font(painter)
            painter.drawText(x, y, txt)
            painter = QtGui.QPainter(self.coords_descr_pix)
            self.prepare_descr_font(painter)
            painter.drawText(x, y, txt)
            # Show what needed
            self.redraw_needed_map()

    def mousePressEvent(self, evt: QtGui.QMouseEvent):
        pix_x = int(round(evt.position().x()))
        pix_y = int(round(evt.position().y()))
        if evt.button() == Qt.MouseButton.RightButton:
            self.on_rightbtn_click(pix_x, pix_y)
            return
        # Otherwise proceed
        map_x = pix_x // self.coord_step
        map_y = pix_y // self.coord_step + 1
        # Show clean map
        self.redraw_needed_map()
        # === Drawing ===
        canvas = self.pixmap()
        painter = QtGui.QPainter(canvas)
        # Draw selected rect
        painter.setPen(self.get_foregnd_pen())
        x = map_x * self.coord_step
        y = (map_y - 1) * self.coord_step
        painter.drawRect(x, y, self.coord_step, self.coord_step)
        painter.end()
        self.setPixmap(canvas)
        # Emit signal
        self.mapclicked.emit(int(map_x), int(map_y))

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
        self.maplbl = MapCanvas()
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
        mapdlg = MapDialog(parent=self)
        mapdlg.exec()
        # self.btnNext.show()
        # self.btnBack.show()
        # self.btnClear.show()
        # self.btn_next_clicked()

    def btn_next_clicked(self):
        # Check if correct data entered
        if self.grpbxs[self.curr_indx] == self.groupBoxQuesse:
            s = '"' + self.lineEditDericol.text().lstrip().rstrip() + '"'
            if check_if_such_dericol_exists(s):
                QMessageBox.warning(self, "Проблема с пером", "Такое перо дериколя уже зарегистрировано.\nВведите идентификатор другого пера.")
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
        line = DataLine()
        # Check if such artid exists
        line.artid = '"' + self.lineEditArtefactID.text().lstrip().rstrip() + '"'
        if check_if_such_artid_exists(line.artid):
            QMessageBox.warning(self, "Проблема с артефактом",
                                "Артефакт с таким идентификатором уже зарегистрирован.\n"
                                "Введите другой идентификатор - возможно, нужно взять из коробки новый.")
            return
        # Add other fields
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

load_database()
load_map_descr()

app = QtWidgets.QApplication([])

window = DiaStart()
window.show()

app.exec()
