from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QDialogButtonBox, QVBoxLayout, QDialog

from kl_strings import clear_string

map_file_name = ".\\img/map.png"

class AnnotationDialog(QDialog):
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

class MapWidget(QtWidgets.QLabel):
    # Constants
    coord_step = 20
    font_sz_pix = 14

    Annotations = []

    def annotations_append_and_save(self, x, y, txt):
        self.Annotations.append([x, y, txt])
        with open(self.Annotns_filename, "a") as datafile:
            datafile.write('"{0}","{1}","{2}"\n'.format(x, y, txt))

    def annotations_load(self):
        self.Annotations.clear()
        try:
            with open(self.Annotns_filename, "r") as datafile:
                lines = datafile.readlines()
            for line in lines:
                chunks = line.split(sep=',')
                if len(chunks) != 3:
                    continue
                x = int(clear_string(chunks[0]))
                y = int(clear_string(chunks[1]))
                txt = clear_string(chunks[2])
                self.Annotations.append([x, y, txt])
        except FileNotFoundError:
            pass

    # Signals
    mapclicked = pyqtSignal(int, int)

    def __init__(self, annotns_filename):
        super().__init__()

        self.Annotns_filename = annotns_filename
        # Pixmaps: clean one, with coords, with description, with both of them
        self.clean_pix = QtGui.QPixmap(map_file_name)
        self.coords_pix = QtGui.QPixmap(map_file_name)
        self.annot_pix = QtGui.QPixmap(map_file_name)
        self.coords_annot_pix = QtGui.QPixmap(map_file_name)
        # Variables
        self.must_show_coords = True
        self.must_show_annot = True
        self.map_x = None
        self.map_y = None
        # Show map primitives
        self.draw_coords(self.coords_pix)
        self.draw_coords(self.coords_annot_pix)
        self.annotations_load()
        self.draw_descr(self.annot_pix)
        self.draw_descr(self.coords_annot_pix)
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
        for d in self.Annotations:
            painter.drawText(d[0], d[1], d[2])
        painter.end()

    def redraw_needed_map(self):
        if self.must_show_coords and self.must_show_annot:
            self.setPixmap(self.coords_annot_pix)
        elif self.must_show_coords:
            self.setPixmap(self.coords_pix)
        elif self.must_show_annot:
            self.setPixmap(self.annot_pix)
        else:
            self.setPixmap(self.clean_pix)

    def draw_rect(self):
        canvas = self.pixmap()
        painter = QtGui.QPainter(canvas)
        # Draw selected rect
        painter.setPen(self.get_foregnd_pen())
        x = self.map_x * self.coord_step
        y = (self.map_y - 1) * self.coord_step
        painter.drawRect(x, y, self.coord_step, self.coord_step)
        painter.end()
        self.setPixmap(canvas)

    def on_map_settings_change(self, show_coords, show_descrip):
        self.must_show_coords = show_coords
        self.must_show_annot = show_descrip
        self.redraw_needed_map()
        # Redraw what selected
        if self.map_x is not None:
            self.draw_rect()

    def on_rightbtn_click(self, x, y):
        dlg = AnnotationDialog(x, y, parent=self)
        if dlg.exec():
            txt = dlg.lineeditDescr.text()
            self.annotations_append_and_save(x, y, txt)
            # Draw on annot and coords_annot
            painter = QtGui.QPainter(self.annot_pix)
            self.prepare_descr_font(painter)
            painter.drawText(x, y, txt)
            painter = QtGui.QPainter(self.coords_annot_pix)
            self.prepare_descr_font(painter)
            painter.drawText(x, y, txt)
            # Show what needed
            self.redraw_needed_map()

    def mousePressEvent(self, evt: QtGui.QMouseEvent):
        pix_x = int(round(evt.x()))
        pix_y = int(round(evt.y()))
        if evt.button() == Qt.MouseButton.RightButton:
            self.on_rightbtn_click(pix_x, pix_y)
            return
        # Otherwise proceed
        self.map_x = pix_x // self.coord_step
        self.map_y = pix_y // self.coord_step + 1
        # Show clean map and draw rect
        self.redraw_needed_map()
        self.draw_rect()
        # Emit signal
        self.mapclicked.emit(self.map_x, self.map_y)
