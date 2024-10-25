import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget,
    QTableWidgetItem, QPushButton, QMenuBar, QAction, QScrollArea, QCheckBox, QLineEdit,
    QFileDialog, QAbstractItemView, QColorDialog
)
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5 import QtGui

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import json
import time

class LabelItem:
    def __init__(self, selected=False, color="#000", name="", tags="", points=[]):
        self.selected = selected
        self.color = color
        self.name = name
        self.tags = tags
        self.points = points

    

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # table items
        self._label_items = [LabelItem() for i in range(10)]

        # image parameters
        self._zoom = None
        self._center = None
        self._points = []
        self._drag = False
        self._image = None

        self.setWindowTitle("Polygonex")
        self.setWindowIcon(QtGui.QIcon(r'C:\Users\gtraw\OneDrive\Pulpit\UM sem. 2\ProjektBadawczy\apps\polygonex\logos\l4.jpg'))
        self.setGeometry(100, 100, 1000, 600)

        # Create main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QHBoxLayout(main_widget)
        right_layout = QVBoxLayout()

        self._canvas = FigureCanvas(Figure(figsize=(16, 8)))
        self._ax = self._canvas.figure.subplots()

        self._canvas.mpl_connect('button_press_event', self.plot_click)
        self._canvas.mpl_connect('motion_notify_event', self.plot_move)
        self._canvas.mpl_connect('button_release_event', self.plot_release)
        self._canvas.mpl_connect('scroll_event', self.plot_scroll)

        select_all_button = QPushButton("Select All")
        select_all_button.clicked.connect(self.select_all_items)

        self.table_widget = QTableWidget(0, 4)
        self.table_widget.setHorizontalHeaderLabels(["Select", "Color", "Name", "Tags"])
        self.table_widget.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setShowGrid(True)
        self.table_widget.setColumnWidth(0, 50)
        self.table_widget.setColumnWidth(1, 50)
        self.table_widget.setColumnWidth(2, 150)
        self.table_widget.setColumnWidth(3, 300)

        self.table_widget.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table_widget.itemChanged.connect(self.handle_item_changed)
        self.table_widget.cellClicked.connect(self.handle_cell_clicked)

        # initial example items
        for i in range(10):
            self.add_item()

        button_1 = QPushButton("Button 1")
        button_1.clicked.connect(self.button_1_clicked)
        button_2 = QPushButton("Button 2")
        button_2.clicked.connect(self.button_2_clicked)
        button_layout = QHBoxLayout()
        button_layout.addWidget(button_1)
        button_layout.addWidget(button_2)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Menu")
        option1 = QAction("Load", self)
        option1.triggered.connect(self.menu_option1_selected)
        option2 = QAction("Save", self)
        option2.triggered.connect(self.menu_option2_selected)
        file_menu.addAction(option1)
        file_menu.addAction(option2)

        right_layout.addWidget(select_all_button)
        right_layout.addWidget(self.table_widget)
        right_layout.addLayout(button_layout)

        main_layout.addWidget(self._canvas)
        main_layout.addLayout(right_layout)

    def add_item(self, selected=False, color="#000", name="", tags="", points=[]):
        new_item = LabelItem(selected, color, name, tags, points)
        self._label_items.append(new_item)
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)
        
        checkbox = QCheckBox()
        checkbox.setChecked(self._label_items[row_position].selected)
        checkbox.stateChanged.connect(lambda state, row=row_position: self.update_item_state(row, "selected", state == Qt.Checked))

        checkbox_widget = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_widget)
        checkbox_layout.addWidget(checkbox)
        checkbox_layout.setAlignment(Qt.AlignCenter)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        checkbox_widget.setLayout(checkbox_layout)
        self.table_widget.setCellWidget(row_position, 0, checkbox_widget)

        name_item = QTableWidgetItem(f"Item {row_position + 1}")
        name_item.setFlags(name_item.flags() | Qt.ItemIsEditable)
        self.table_widget.setItem(row_position, 2, name_item)

        desc_item = QTableWidgetItem(f"Description {row_position + 1}")
        desc_item.setFlags(desc_item.flags() | Qt.ItemIsEditable)
        self.table_widget.setItem(row_position, 3, desc_item)

        color_item = QTableWidgetItem()
        color_item.setFlags(Qt.ItemIsEnabled)
        self.table_widget.setItem(row_position, 1, color_item)
        print("new item added")

    def update_item_state(self, row, field, value):
        if field == "selected":
            self._label_items[row].selected = value
        elif field == "name":
            self._label_items[row].name = value
        elif field == "tags":
            self._label_items[row].tags = value

    def handle_item_changed(self, item):
        row = item.row()
        col = item.column()
        print(f"item [{row}, {col}] changed")

        if col == 1:
            self._label_items[row].name = item.text()
        elif col == 2:
            self._label_items[row].tags = item.text()

    def handle_cell_clicked(self, row, column):
        print(f"cell in row {row} clicked")
        if column == 1:
            self.select_color(row)

    def select_all_items(self):
        for row in range(self.table_widget.rowCount()):
            checkbox_widget = self.table_widget.cellWidget(row, 0)
            checkbox = checkbox_widget.layout().itemAt(0).widget()
            checkbox.setChecked(True)
            self.update_item_state(row, "selected", True)

    def plot_click(self, event):
        x, y = event.xdata, event.ydata
        print("clicked", event.button, x, y)
        if x is not None and y is not None:
            # LMB - add point to polygon
            if event.button == 1:
                if self._points:
                    self._ax.plot([self._points[-1][0], x], [self._points[-1][1], y], 'r-')
                    if self._point_tmp:
                        self._point_tmp[0].remove()
                        self._point_tmp = None
                else:
                    self._point_tmp = self._ax.plot(x, y, 'ro')
                self._points.append([x, y])
                self._canvas.draw()

            # wheel button
            elif event.button == 2:
                self.press_pos = (event.xdata, event.ydata)
                self._drag = True

            # RMB - end of sequence
            elif event.button == 3:
                self.add_item(points=self._points)
                self._points = []
                self.display_image()

        # self.update_image()

    def plot_release(self, event):
        if event.button == 2:
            self._drag = False

    def plot_move(self, event):
        pass

    def plot_scroll(self, event):
        print("scroll", event.step, event.xdata, event.ydata)
        self._zoom = max(1, self._zoom - event.step / 4)
        self._mouse_position = [event.xdata, event.ydata]
        self.update_image()

    def button_1_clicked(self):
        print("Button 1 clicked")

    def button_2_clicked(self):
        print("Button 2 clicked")

    def menu_option1_selected(self):
        print("Load option selected")
        self._image_path = QFileDialog.getOpenFileName(self, 'Load file', '', "Parking images (*.jpg *.png)")[0]
        if self._image_path:
            self._image = mpimg.imread(self._image_path)
            image_name = self._image_path
            for sep in ['\\']:
                image_name = image_name.replace(sep, '/')
            image_name = ''.join(image_name.split('/')[-1].split('.')[:-1])
            self._image_name = image_name
            
            self.display_image()

    def menu_option2_selected(self):
        print("Save option selected")

    def display_image(self):
        if self._image is not None:
            self._ax.clear()
            self._ax.imshow(self._image)
            self._canvas.draw()

            self._center = [self._image.shape[0] // 2, self._image.shape[1] // 2]
            self._zoom = 1
            self.press_pos = None

    def update_image(self):
        print(f"Updating plot image...")
        # use zoom
        mouse_x, mouse_y = self._mouse_position
        zoom = 1 + ((self._zoom - 1) / 2) ** 2
        height_img, width_img, _ = self._image.shape
        height_zoomed = height_img // zoom // 2
        width_zoomed = width_img // zoom // 2

        x_lims, y_lims = self._ax.get_xlim(), self._ax.get_ylim()
        w1 = (x_lims[1] - x_lims[0]) / 2
        h1 = (y_lims[0] - y_lims[1]) / 2

        mouse_diff = [mouse_x - self._center[0], mouse_y - self._center[1]] # [cmx, cmy]
        mouse_diff_new = [width_zoomed / w1 * mouse_diff[0], height_zoomed / h1 * mouse_diff[1]]

        self._center = [self._mouse_position[i] - mouse_diff_new[i] for i in range(2)]

        # fit lims in image shape
        self._center[0] = min(max(width_zoomed, self._center[0]), width_img - width_zoomed)
        self._center[1] = min(max(height_zoomed, self._center[1]), height_img - height_zoomed)

        self._ax.set_xlim(self._center[0] - width_zoomed, self._center[0] + width_zoomed)
        self._ax.set_ylim(self._center[1] + height_zoomed, self._center[1] - height_zoomed)    

        self._canvas.draw()

    def select_color(self, row):
        color = QColorDialog.getColor()

        if color.isValid():
            color_item = QTableWidgetItem()
            color_item.setBackground(color)
            self.table_widget.setItem(row, 1, color_item)
            self._label_items[row].color = color.name()
            
            print(f"Color for row {row} selected: {color.name()}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())