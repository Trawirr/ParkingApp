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
    def __init__(self, selected=False, name="", tags=""):
        self.selected = selected
        self.name = name
        self.tags = tags

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # table items
        self._label_items = [LabelItem() for i in range(10)]

        # image parameters
        self._zoom = None
        self._center = None
        self._points = []

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
        self._canvas.mpl_connect('scroll_event', self.plot_scroll)

        select_all_button = QPushButton("Select All")
        select_all_button.clicked.connect(self.select_all_items)

        self.table_widget = QTableWidget(10, 4)
        self.table_widget.setHorizontalHeaderLabels(["Select", "Color", "Name", "Tags"])
        self.table_widget.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setColumnWidth(0, 50)
        self.table_widget.setColumnWidth(1, 50)
        self.table_widget.setColumnWidth(2, 150)
        self.table_widget.setColumnWidth(3, 500)

        self.table_widget.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table_widget.itemChanged.connect(self.handle_item_changed)
        self.table_widget.cellClicked.connect(self.handle_cell_clicked)

        # initial example items
        for i in range(10):
            checkbox = QCheckBox()
            checkbox.setChecked(self._label_items[i].selected)
            checkbox.stateChanged.connect(lambda state, row=i: self.update_item_state(row, "selected", state == Qt.Checked))

            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_widget.setLayout(checkbox_layout)
            self.table_widget.setCellWidget(i, 0, checkbox_widget)

            color_item = QTableWidgetItem()
            color_item.setFlags(Qt.ItemIsEnabled)
            self.table_widget.setItem(i, 1, color_item)

            item_name = QTableWidgetItem(self._label_items[i].name or f"Item {i + 1}")
            item_name.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            self.table_widget.setItem(i, 2, item_name)

            tags = QTableWidgetItem(self._label_items[i].tags or f"Tags {i + 1}")
            tags.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            self.table_widget.setItem(i, 3, tags)

        # Buttons under the list
        button_1 = QPushButton("Button 1")
        button_1.clicked.connect(self.button_1_clicked)
        button_2 = QPushButton("Button 2")
        button_2.clicked.connect(self.button_2_clicked)
        button_layout = QHBoxLayout()
        button_layout.addWidget(button_1)
        button_layout.addWidget(button_2)

        # Menu with two options
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
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

            # RMB - end of sequence
            elif event.button == 3:
                pass

        self.update_image()

    def plot_scroll(self, event):
        print("scroll", event.step, event.xdata, event.ydata)
        self._zoom = max(1, self._zoom + event.step)
        self._center = [event.xdata, event.ydata]
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

    def update_image(self):
        print(f"updating: {self._center=}, {self._zoom=}")
        # use zoom
        height_img, width_img, _ = self._image.shape
        height_zoomed = height_img // self._zoom // 2
        width_zoomed = width_img // self._zoom // 2
        print(f"{height_img=}, {width_img=}, {self._zoom=} => {height_zoomed=}, {width_zoomed=}")

        print(f"before {self._center=}")
        # fix x
        self._center[0] += min(0, width_zoomed - self._center[0])
        self._center[0] -= min(0, self._center[0] + width_zoomed - width_img)

        # fix y
        self._center[1] += min(0, height_zoomed - self._center[1])
        self._center[1] -= min(0, self._center[1] + height_zoomed - height_img)
        print(f"after {self._center=}")

        # set lims
        self._ax.set_xlim(self._center[0] - width_zoomed, self._center[0] + width_zoomed)
        self._ax.set_ylim(self._center[1] + height_zoomed, self._center[1] - height_zoomed)        

        # draw updated image
        self._canvas.draw()

    def select_color(self, row):
        """Open a color dialog and set the selected color in the row."""
        color = QColorDialog.getColor()

        if color.isValid():
            # Update the background color of the row (color column)
            color_item = QTableWidgetItem()
            color_item.setBackground(color)
            self.table_widget.setItem(row, 1, color_item)
            
            print(f"Color for row {row} selected: {color.name()}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())