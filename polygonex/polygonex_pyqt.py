import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget,
    QTableWidgetItem, QPushButton, QMenuBar, QAction, QScrollArea, QCheckBox, QLineEdit,
    QFileDialog, 
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

        self.label_items = [LabelItem() for i in range(10)]

        self.setWindowTitle("Polygonex")
        self.setWindowIcon(QtGui.QIcon(r'C:\Users\gtraw\OneDrive\Pulpit\UM sem. 2\ProjektBadawczy\apps\polygonex\logos\l4.jpg'))
        self.setGeometry(100, 100, 1000, 600)

        # Create main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QHBoxLayout(main_widget)
        right_layout = QVBoxLayout()

        self.canvas = FigureCanvas(Figure(figsize=(18, 8)))
        self.ax = self.canvas.figure.subplots()
        self.ax.plot([0, 1, 2], [0, 1, 4])

        self.canvas.mpl_connect('button_press_event', self.plot_click)
        self.canvas.mpl_connect('scroll_event', self.plot_scroll)

        select_all_button = QPushButton("Select All")
        select_all_button.clicked.connect(self.select_all_items)

        self.table_widget = QTableWidget(10, 3)
        self.table_widget.setHorizontalHeaderLabels(["Select", "Name", "Tags"])
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setColumnWidth(0, 50)
        self.table_widget.setColumnWidth(1, 150)
        self.table_widget.setColumnWidth(2, 500)

        self.table_widget.itemChanged.connect(self.handle_item_changed)

        for i in range(10):
            checkbox = QCheckBox()
            checkbox.setChecked(self.label_items[i].selected)
            checkbox.stateChanged.connect(lambda state, row=i: self.update_item_state(row, "selected", state == Qt.Checked))

            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_widget.setLayout(checkbox_layout)
            self.table_widget.setCellWidget(i, 0, checkbox_widget)

            item_name = QTableWidgetItem(self.label_items[i].name or f"Item {i + 1}")
            item_name.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            self.table_widget.setItem(i, 1, item_name)

            tags = QTableWidgetItem(self.label_items[i].tags or f"Tags {i + 1}")
            tags.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            self.table_widget.setItem(i, 2, tags)

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

        main_layout.addWidget(self.canvas)
        main_layout.addLayout(right_layout)

    def update_item_state(self, row, field, value):
        if field == "selected":
            self.label_items[row].selected = value
        elif field == "name":
            self.label_items[row].name = value
        elif field == "tags":
            self.label_items[row].tags = value

    def handle_item_changed(self, item):
        row = item.row()
        col = item.column()

        if col == 1:
            self.label_items[row].name = item.text()
        elif col == 2:
            self.label_items[row].tags = item.text()

    def select_all_items(self):
        for row in range(self.table_widget.rowCount()):
            checkbox_widget = self.table_widget.cellWidget(row, 0)
            checkbox = checkbox_widget.layout().itemAt(0).widget()
            checkbox.setChecked(True)
            self.update_item_state(row, "selected", True)

    def plot_click(self, event):
        print("plot click")

    def plot_scroll(self, event):
        print("plot scroll")

    def button_1_clicked(self):
        print("Button 1 clicked")

    def button_2_clicked(self):
        print("Button 2 clicked")

    def menu_option1_selected(self):
        print("Load option selected")
        self.image_path = QFileDialog.getOpenFileName(self, 'Load file', '', "Parking images (*.jpg *.png)")[0]
        if self.image_path:
            self.image = mpimg.imread(self.image_path)
            print(f"selected image: {self.image_path=}")
            image_name = self.image_path
            for sep in ['\\']:
                image_name = image_name.replace(sep, '/')
            image_name = ''.join(image_name.split('/')[-1].split('.')[:-1])
            self.image_name = image_name
            
            self.update_image()

    def menu_option2_selected(self):
        print("Save option selected")

    def update_image(self):
        if self.image is not None:
            self.ax.clear()
            self.ax.imshow(self.image)
            self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())