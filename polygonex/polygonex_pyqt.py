import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget,
    QTableWidgetItem, QPushButton, QMenuBar, QAction, QScrollArea, QCheckBox, QLineEdit,
    QFileDialog, QAbstractItemView, QColorDialog, QMessageBox, QGroupBox,
    QRadioButton
)
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5 import QtGui

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import json
import time
import os

class LabelItem:
    def __init__(self, id=0, selected=False, color="#000", name="", tags="", points=[]):
        self.id = id
        self.selected = selected
        self.color = color
        self.name = name
        self.tags = tags
        self.points = points

    @property
    def points_number(self):
        return len(self.points)

class ClickableCheckboxWidget(QWidget):
    def __init__(self, checkbox, parent=None):
        super().__init__(parent)
        self.checkbox = checkbox
        layout = QHBoxLayout(self)
        layout.addWidget(self.checkbox)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def mousePressEvent(self, event):
        # Toggle checkbox state when cell is clicked
        self.checkbox.setChecked(not self.checkbox.isChecked())
        super().mousePressEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # table items
        self._label_items = []
        self._polygons = {}
        self._item_counter = 0

        # image parameters
        self._zoom = None
        self._center = None
        self._points = []
        self._drag = False
        self._image = None
        self._image_path = None
        self._image_name = None

        self.setWindowTitle("Polygonex")
        self.setWindowIcon(QtGui.QIcon(r'C:\Users\gtraw\OneDrive\Pulpit\UM sem. 2\ProjektBadawczy\apps\polygonex\logos\l4.jpg'))
        self.setGeometry(100, 100, 1000, 600)

        # main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QHBoxLayout(main_widget)
        right_layout = QVBoxLayout()

        # matplotlib canvas
        self._canvas = FigureCanvas(Figure(figsize=(15, 8)))
        self._ax = self._canvas.figure.subplots()

        self._canvas.mpl_connect('button_press_event', self.plot_click)
        self._canvas.mpl_connect('motion_notify_event', self.plot_move)
        self._canvas.mpl_connect('button_release_event', self.plot_release)
        self._canvas.mpl_connect('scroll_event', self.plot_scroll)

        self._select_all_button = QPushButton("Select all")
        self._select_all_button.clicked.connect(self.select_all_items)

        self.table_widget = QTableWidget(0, 5)
        self.table_widget.setHorizontalHeaderLabels(["Select", "Color", "Name", "Tags", ""])
        self.table_widget.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setShowGrid(True)
        self.table_widget.setColumnWidth(0, 50)
        self.table_widget.setColumnWidth(1, 50)
        self.table_widget.setColumnWidth(2, 150)
        self.table_widget.setColumnWidth(3, 500)

        self.table_widget.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table_widget.itemChanged.connect(self.handle_item_changed)
        self.table_widget.cellClicked.connect(self.handle_cell_clicked)

        self.table_widget.setSelectionMode(QAbstractItemView.NoSelection)
        self.table_widget.setFocusPolicy(Qt.NoFocus)

        button_1 = QPushButton("Button 1")
        button_1.clicked.connect(self.button_1_clicked)
        button_2 = QPushButton("Button 2")
        button_2.clicked.connect(self.button_2_clicked)
        button_layout = QHBoxLayout()
        button_layout.addWidget(button_1)
        button_layout.addWidget(button_2)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Menu")
        option1 = QAction("Load image", self)
        option1.triggered.connect(self.menu_option_load_image)
        option2 = QAction("Load json", self)
        option2.triggered.connect(self.menu_option_load_json)
        option3 = QAction("Save json", self)
        option3.triggered.connect(self.menu_option_save)
        file_menu.addAction(option1)
        file_menu.addAction(option2)
        file_menu.addAction(option3)
        
        # radio buttons
        radio_buttons_layout = self.create_radio_buttons()
        right_layout.addLayout(radio_buttons_layout)

        right_layout.addWidget(self._select_all_button)
        right_layout.addWidget(self.table_widget)
        right_layout.addLayout(button_layout)

        main_layout.addWidget(self._canvas)
        main_layout.addLayout(right_layout)

        right_layout.addWidget(self._select_all_button)
        right_layout.addWidget(self.table_widget)
        right_layout.addLayout(button_layout)

        main_layout.addWidget(self._canvas)
        main_layout.addLayout(right_layout)

    def create_radio_buttons(self):
        layout = QVBoxLayout()

        # Group 1: Time of Day
        time_group = QGroupBox("Time of Day")
        time_layout = QVBoxLayout()
        day_radio = QRadioButton("Day")
        evening_radio = QRadioButton("Evening")
        night_radio = QRadioButton("Night")
        time_layout.addWidget(day_radio)
        time_layout.addWidget(evening_radio)
        time_layout.addWidget(night_radio)
        time_group.setLayout(time_layout)

        # Group 2: Weather Condition
        weather_group = QGroupBox("Weather")
        weather_layout = QVBoxLayout()
        sunny_radio = QRadioButton("Sunny")
        cloudy_radio = QRadioButton("Cloudy")
        weather_layout.addWidget(sunny_radio)
        weather_layout.addWidget(cloudy_radio)
        weather_group.setLayout(weather_layout)

        # Group 3: Precipitation
        precipitation_group = QGroupBox("Precipitation")
        precipitation_layout = QVBoxLayout()
        rain_radio = QRadioButton("Rain")
        snow_radio = QRadioButton("Snow")
        fog_radio = QRadioButton("Fog")
        none_radio = QRadioButton("None")
        precipitation_layout.addWidget(rain_radio)
        precipitation_layout.addWidget(snow_radio)
        precipitation_layout.addWidget(fog_radio)
        precipitation_layout.addWidget(none_radio)
        precipitation_group.setLayout(precipitation_layout)

        # Add groups to the main layout
        layout.addWidget(time_group)
        layout.addWidget(weather_group)
        layout.addWidget(precipitation_group)

        return layout

    def add_item(self, selected=False, color="#000", name="", tags="", points=[]):
        self._item_counter += 1
        print(f"adding item, id={self._item_counter} {selected=}, {color=}, {name=}, {tags=}, {points=}")
        new_item = LabelItem(self._item_counter, selected, color, name, tags, points)
        self._label_items.append(new_item)
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)
        
        checkbox = QCheckBox()
        checkbox.setChecked(self._label_items[row_position].selected)
        checkbox.stateChanged.connect(lambda state, row=row_position: self.update_item_state(row, "selected", state == Qt.Checked))

        checkbox_widget = ClickableCheckboxWidget(checkbox)
        
        self.table_widget.setCellWidget(row_position, 0, checkbox_widget)

        name_item = QTableWidgetItem(f"{name or f'Item {self._item_counter}'}")
        name_item.setFlags(name_item.flags() | Qt.ItemIsEditable)
        self.table_widget.setItem(row_position, 2, name_item)

        desc_item = QTableWidgetItem(f"{tags or f'Tags {self._item_counter}'}")
        desc_item.setFlags(desc_item.flags() | Qt.ItemIsEditable)
        self.table_widget.setItem(row_position, 3, desc_item)

        color_item = QTableWidgetItem()
        color_item.setFlags(Qt.ItemIsEnabled)
        color_item.setBackground(QtGui.QColor(color))
        self.table_widget.setItem(row_position, 1, color_item)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda _, row=row_position: self.confirm_delete_item(row))
        self.table_widget.setCellWidget(row_position, 4, delete_button)

        print("new item added")
        self.update_select_all_button()

    def confirm_delete_item(self, row):
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this item?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.delete_item(row)

    def delete_item(self, row):
        if row < len(self._label_items):
            self.remove_polygon(row)
            self._label_items.pop(row)
        self.table_widget.removeRow(row)
        print(f"Item at row {row} deleted")
        
        # fix delete buttons' connections
        for i in range(row, self.table_widget.rowCount()):
            delete_button = self.table_widget.cellWidget(i, 4)
            if delete_button is not None:
                delete_button.clicked.disconnect() 
                delete_button.clicked.connect(lambda _, row=i: self.confirm_delete_item(row))

        # fix checkboxes' connections
        for i in range(row, self.table_widget.rowCount()):
            checkbox = self.table_widget.cellWidget(i, 0).layout().itemAt(0).widget()
            if checkbox is not None:
                checkbox.stateChanged.disconnect() 
                checkbox.stateChanged.connect(lambda state, row=i: self.update_item_state(row, "selected", state == Qt.Checked))

    # update one of item's fields
    def update_item_state(self, row, field, value):
        if field == "selected":
            self._label_items[row].selected = value
            if value:
                self.add_polygon(row)
            else:
                self.remove_polygon(row)
            self.update_select_all_button()
        elif field == "name":
            self._label_items[row].name = value
        elif field == "tags":
            self._label_items[row].tags = value
        print("updated:", row, field, value, self._label_items[row])

    # convert all label items to dict
    def label_items_to_dict(self):
        return [
            {
                "name": item.name,
                "color": item.color,
                "tags": item.tags,
                "points": item.points
            }
            for item in self._label_items
        ]
    
    # save label items to json file with the same path as image file
    def save_label_items(self):
        json_filename = os.path.join(
            os.path.dirname(self._image_path), f"{self._image_name}.json"
        )
        print(json_filename)

        label_items_data = self.label_items_to_dict()
        print("\nsaving:", label_items_data)
        with open(json_filename, "w") as json_file:
            json.dump(label_items_data, json_file, indent=4)
        
        print(f"Label items saved to {json_filename}")

    # clear table, label items list and load label items from json file
    def load_label_items(self, json_path):
        try:
            with open(json_path, "r") as json_file:
                label_data = json.load(json_file)
            
            self._label_items.clear()
            self.table_widget.setRowCount(0)
            
            for row, item_data in enumerate(label_data):
                print("item data:", item_data)
                name = item_data.get("name", "")
                color = item_data.get("color", "#000")
                tags = item_data.get("tags", "")
                points = item_data.get("points", [])

                self.add_item(selected=False, color=color, name=name, tags=tags, points=points)
                print(f"loading item, {color=}, {name=}, {tags=}, {points=}")
            
            print(f"Loaded label items from {json_path}")

        except Exception as e:
            print(f"Failed to load label items: {e}")

    # draw and save polygon for given label item
    def add_polygon(self, row):
        item = self._label_items[row]
        if item.points_number > 1:
            polygon = plt.Polygon(item.points, closed=True, color=item.color, alpha=0.5)
            self._ax.add_patch(polygon)
            self._polygons[item.id] = polygon
            self._canvas.draw()
            print(f"Polygon added for row {row}")
        if item.points_number == 1:
            point = plt.Circle((item.points[0][0], item.points[0][1]), radius=5, color=item.color, alpha=0.75)
            self._ax.add_patch(point)
            self._polygons[item.id] = point
            self._canvas.draw()
            print(f"Point added for row {row}")

    # remove polygon for given label item
    def remove_polygon(self, row):
        item = self._label_items[row]
        if item.id in self._polygons:
            polygon = self._polygons.pop(item.id)
            polygon.remove()
            self._canvas.draw()
            print(f"Polygon removed for row {row}")

    # remove polygons for all label items
    def remove_all_polygons(self):
        rows = list(self._polygons.keys())
        for row in rows:
            self.remove_polygon(row)
        print("Removed all polygons")

    # update label item's text fields
    def handle_item_changed(self, item):
        row = item.row()
        col = item.column()
        print(f"item [{row}, {col}] changed")

        if col == 2:
            self._label_items[row].name = item.text()
        elif col == 3:
            self._label_items[row].tags = item.text()

    # handle click on checkbox cell
    def handle_cell_clicked(self, row, column):
        print(f"cell in row {row} clicked")
        if column == 1:
            self.select_color(row)

            checkbox_widget = self.table_widget.cellWidget(row, 0)
            checkbox = checkbox_widget.layout().itemAt(0).widget()
            if checkbox.isChecked():
                self.remove_polygon(row)
                self.add_polygon(row)

    def select_all_items(self):
        select_mode = True if self._select_all_button.text() == "Select all" else False
        for row in range(self.table_widget.rowCount()):
            checkbox_widget = self.table_widget.cellWidget(row, 0)
            checkbox = checkbox_widget.layout().itemAt(0).widget()
            checkbox.setChecked(select_mode)
        self.update_select_all_button()

    def update_select_all_button(self):
        all_selected = True
        for row in range(self.table_widget.rowCount()):
            checkbox_widget = self.table_widget.cellWidget(row, 0)
            checkbox = checkbox_widget.layout().itemAt(0).widget()
            if not checkbox.isChecked():
                all_selected = False
                break
        if all_selected:
            self._select_all_button.setText("Unselect all")
        else:
            self._select_all_button.setText("Select all")

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
                self.add_item(selected=True, points=self._points)
                self._points = []
                self.display_image()

        # self.update_image()

    def plot_release(self, event):
        if event.button == 3:
            self._drag = False

    def plot_move(self, event):
        if self._image is not None:
            if self._drag and self.press_pos and event.xdata is not None and event.ydata is not None:
                print("event", event.xdata, event.ydata)
                dx = event.xdata - self.press_pos[0]
                dy = event.ydata - self.press_pos[1]
                self.press_pos = (event.xdata, event.ydata)
                print("dx dy", dx, dy)

                self._ax.set_xlim(self._ax.get_xlim() - dx)
                self._ax.set_ylim(self._ax.get_ylim() - dy)
                self._center = [sum(self._ax.get_xlim()) / 2, sum(self._ax.get_ylim()) / 2]

                self._canvas.draw()
            if not self.press_pos and event.xdata is not None and event.ydata is not None:
                self.press_pos = (event.xdata, event.ydata)

    def plot_scroll(self, event):
        print("scroll", event.step, event.xdata, event.ydata)
        self._zoom = max(1, self._zoom - event.step / 4)
        self._mouse_position = [event.xdata, event.ydata]
        self.update_image()

    def button_1_clicked(self):
        print("Button 1 clicked")

    def button_2_clicked(self):
        print("Button 2 clicked")

    def menu_option_load_image(self):
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

    def menu_option_load_json(self):
        print("Load Label Items option selected")
        json_path = QFileDialog.getOpenFileName(self, 'Load Label Items', '', "JSON files (*.json)")[0]
        if json_path:
            self.load_label_items(json_path)
            self.remove_all_polygons()

    def menu_option_save(self):
        print("Save option selected")
        self.save_label_items()

    def display_image(self):
        if self._image is not None:
            self._ax.clear()
            self._ax.imshow(self._image)
            self._canvas.draw()

            self._center = [self._image.shape[0] // 2, self._image.shape[1] // 2]
            self._zoom = 1
            self.press_pos = None
        
        self.remove_all_polygons()
        self._polygons = {}
        for row in range(self.table_widget.rowCount()):
            checkbox_widget = self.table_widget.cellWidget(row, 0)
            checkbox = checkbox_widget.layout().itemAt(0).widget()
            if checkbox.isChecked():
                self.add_polygon(row)

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