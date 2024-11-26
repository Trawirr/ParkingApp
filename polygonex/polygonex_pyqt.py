import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTableWidget,
    QTableWidgetItem, QPushButton, QMenuBar, QAction, QScrollArea, QCheckBox, QLineEdit,
    QFileDialog, QAbstractItemView, QColorDialog, QMessageBox, QGroupBox,
    QRadioButton, QButtonGroup, QLabel, QGridLayout, QShortcut, QComboBox
)
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5 import QtGui

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from shapely.geometry import Polygon
from shapely.ops import unary_union
import numpy as np
import cv2
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

        self._last_action = '---'
        self._save_path = None

        # table items
        self._label_items = []
        self._polygons = {}
        self._item_counter = 0

        # image parameters
        self._zoom = None
        self._center = None
        self._points = []
        self._line_plots = []
        self._drag = False
        self._image = None
        self._image_path = None
        self._image_name = None
        self._brightness = 0

        self.setWindowTitle("Polygonex")
        self.setGeometry(100, 100, 1000, 600)

        # main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout(main_widget)
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)
        left_layout = QVBoxLayout()

        # matplotlib canvas
        self._canvas = FigureCanvas(Figure(figsize=(15, 8)))
        self._ax = self._canvas.figure.subplots()

        self._canvas.mpl_connect('button_press_event', self.plot_click)
        self._canvas.mpl_connect('button_release_event', self.plot_release)
        self._canvas.mpl_connect('scroll_event', self.plot_scroll)

        self._select_all_button = QPushButton("Select all")
        self._select_all_button.clicked.connect(self.select_all_items)

        self.table_widget = QTableWidget(0, 5)
        self.table_widget.setHorizontalHeaderLabels(["Del", "Select", "Color", "Name", "Tags"])
        self.table_widget.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setShowGrid(True)
        self.table_widget.setColumnWidth(0, 50)
        self.table_widget.setColumnWidth(1, 50)
        self.table_widget.setColumnWidth(2, 50)
        self.table_widget.setColumnWidth(3, 100)
        self.table_widget.setColumnWidth(4, 200)

        self.table_widget.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table_widget.itemChanged.connect(self.handle_item_changed)
        self.table_widget.cellClicked.connect(self.handle_cell_clicked)

        self.table_widget.setSelectionMode(QAbstractItemView.NoSelection)
        self.table_widget.setFocusPolicy(Qt.NoFocus)

        # buttons above the table
        # button_1 = QPushButton("Button 1")
        # button_1.clicked.connect(self.button_1_clicked)
        # button_2 = QPushButton("Button 2")
        # button_2.clicked.connect(self.button_2_clicked)
        # button_layout = QHBoxLayout()
        # button_layout.addWidget(button_1)
        # button_layout.addWidget(button_2)

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
        self.weather_groupbox = QGroupBox("Weather Conditions")
        self.weather_layout = QGridLayout()

        time_label = QLabel("Brightness")
        self.weather_layout.addWidget(time_label, 0, 0)
        self.brightness_buttons = QButtonGroup(self)
        for i, l in enumerate(["bright", "dark", "night"]):
            new_radio_button = QRadioButton(l)
            self.brightness_buttons.addButton(new_radio_button, id=i + 1)
            if i == 0:
                new_radio_button.setChecked(True)
            self.weather_layout.addWidget(new_radio_button, i + 1, 0)

        precipitation_label = QLabel("Precipitation")
        self.weather_layout.addWidget(precipitation_label, 0, 1)
        self.precipitation_buttons = QButtonGroup(self)
        for i, l in enumerate(["none", "rainfall", "snowfall", "fog"]):
            new_radio_button = QRadioButton(l)
            self.precipitation_buttons.addButton(new_radio_button, id=i + 1)
            if i == 0:
                new_radio_button.setChecked(True)
            self.weather_layout.addWidget(new_radio_button, i + 1, 1)

        surface_label = QLabel("Surface")
        self.weather_layout.addWidget(surface_label, 0, 2)
        self.surface_buttons = QButtonGroup(self)
        for i, l in enumerate(["none", "puddles", "snow"]):
            new_radio_button = QRadioButton(l)
            self.surface_buttons.addButton(new_radio_button, id=i + 1)
            if i == 0:
                new_radio_button.setChecked(True)
            self.weather_layout.addWidget(new_radio_button, i + 1, 2)
    
        weather_label = QLabel("Weather")
        self.weather_layout.addWidget(weather_label, 0, 3)
        self.weather_buttons = QButtonGroup(self)
        for i, l in enumerate(["none", "sunny", "cloudy"]):
            new_radio_button = QRadioButton(l)
            self.weather_buttons.addButton(new_radio_button, id=i + 1)
            if i == 0:
                new_radio_button.setChecked(True)
            self.weather_layout.addWidget(new_radio_button, i + 1, 3)

        self.brightness_buttons.buttonClicked.connect(self.radio_button_click)
        self.precipitation_buttons.buttonClicked.connect(self.radio_button_click)
        self.weather_buttons.buttonClicked.connect(self.radio_button_click)

        self.weather_groupbox.setFixedWidth(400)
        self.table_widget.setFixedWidth(400)
        self.weather_groupbox.setLayout(self.weather_layout)
        left_layout.addWidget(self.weather_groupbox)

        left_layout.addWidget(self._select_all_button)
        left_layout.addWidget(self.table_widget)
        # left_layout.addLayout(button_layout)

        content_layout.addLayout(left_layout)
        content_layout.addWidget(self._canvas)

        # status label
        self._status_label = QLabel("")
        self._status_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(self._status_label)

        # shortcuts
        self.save_shortcut = QShortcut(QtGui.QKeySequence('CTRL+S'), self)
        self.save_shortcut.activated.connect(self.menu_option_save)
        self.save_shortcut = QShortcut(QtGui.QKeySequence('CTRL+Z'), self)
        self.save_shortcut.activated.connect(self.undo_point)

        # intersection removal
        self.top_polygon_selector = QComboBox()
        self.bottom_polygon_selector = QComboBox()
        self.subtract_button = QPushButton("Subtract Intersection")
        self.subtract_button.clicked.connect(self.subtract_intersection)

        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Top Polygon:"))
        selector_layout.addWidget(self.top_polygon_selector)
        selector_layout.addWidget(QLabel("Bottom Polygon:"))
        selector_layout.addWidget(self.bottom_polygon_selector)

        left_layout.addLayout(selector_layout)
        left_layout.addWidget(self.subtract_button)

        self.update_status()

    # updating intersection comboboxes
    def update_polygon_selectors(self):
        self.top_polygon_selector.clear()
        self.bottom_polygon_selector.clear()

        for item in self._label_items:
            self.top_polygon_selector.addItem(item.name, item.id)
            self.bottom_polygon_selector.addItem(item.name, item.id)

    # deleting intersection of two selected polygons from the 'bottom' one
    def subtract_intersection(self):
        top_id = self.top_polygon_selector.currentData()
        bottom_id = self.bottom_polygon_selector.currentData()

        if top_id is None or bottom_id is None:
            QMessageBox.warning(self, "Warning", "Please select both top and bottom polygons.")
            return

        top_item = next((item for item in self._label_items if item.id == top_id), None)
        bottom_item = next((item for item in self._label_items if item.id == bottom_id), None)

        if not top_item or not bottom_item:
            QMessageBox.warning(self, "Warning", "Invalid polygon selection.")
            return

        if not len(top_item.points) > 2 or not len(bottom_item.points) > 2:
            QMessageBox.warning(self, "Warning", "Both polygons must have defined points.")
            return
        
        confirm = QMessageBox.question(
            self,
            "Confirm Subtraction",
            f"Are you sure you want to subtract the intersection of '{top_item.name}' from '{bottom_item.name}'?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if confirm != QMessageBox.Yes:
            return

        top_polygon = Polygon(top_item.points)
        bottom_polygon = Polygon(bottom_item.points)

        if not top_polygon.is_valid or not bottom_polygon.is_valid:
            QMessageBox.warning(self, "Warning", "One or both polygons are invalid.")
            return

        result_polygon = bottom_polygon.difference(top_polygon)

        if result_polygon.is_empty:
            bottom_item.points = []
        else:
            bottom_item.points = list(result_polygon.exterior.coords)

        self.remove_polygon(self._label_items.index(bottom_item))
        self.add_polygon(self._label_items.index(bottom_item))

        self._last_action = f"intersection subtracted ({top_item.name=}, {bottom_item.name=})"
        self.update_status()

    def update_status(self):
        self._status_label.setText(f"image: {self._image_name} | brightness: {self._brightness:.3f} | last: {self._last_action}")

    def add_item(self, selected=False, color="#000", name="", tags="", points=[]):
        self._item_counter += 1
        print(f"adding item, id={self._item_counter} {selected=}, {color=}, {name=}, {tags=}, {points=}")
        new_item = LabelItem(self._item_counter, selected, color, name, tags, points)
        self._label_items.append(new_item)
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)
        
        checkbox = QCheckBox()
        checkbox.setChecked(self._label_items[row_position].selected)
        checkbox.stateChanged.connect(lambda state, row=row_position: self.update_item_state(row, state == Qt.Checked))

        checkbox_widget = ClickableCheckboxWidget(checkbox)
        
        self.table_widget.setCellWidget(row_position, 1, checkbox_widget)

        name_item = QTableWidgetItem(f"{name or f'Item {self._item_counter}'}")
        name_item.setFlags(name_item.flags() | Qt.ItemIsEditable)
        self.table_widget.setItem(row_position, 3, name_item)

        desc_item = QTableWidgetItem(f"{tags or f'Tags {self._item_counter}'}")
        desc_item.setFlags(desc_item.flags() | Qt.ItemIsEditable)
        self.table_widget.setItem(row_position, 4, desc_item)

        color_item = QTableWidgetItem()
        color_item.setFlags(Qt.ItemIsEnabled)
        color_item.setBackground(QtGui.QColor(color))
        self.table_widget.setItem(row_position, 2, color_item)

        delete_button = QPushButton("X")
        delete_button.clicked.connect(lambda _, id=new_item.id: self.confirm_delete_item(id))
        self.table_widget.setCellWidget(row_position, 0, delete_button)

        print("new item added")
        self.update_select_all_button()
        self.update_polygon_selectors()

        self._last_action = f'item {name_item.text()} added'
        self.update_status()

    def confirm_delete_item(self, id):
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this item?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.delete_item(id)

    def delete_item(self, id):
        for r, li in enumerate(self._label_items):
            if id == li.id:
                row = r
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
            checkbox = self.table_widget.cellWidget(i, 1).layout().itemAt(0).widget()
            if checkbox is not None:
                checkbox.stateChanged.disconnect() 
                checkbox.stateChanged.connect(lambda state, row=i: self.update_item_state(row, state == Qt.Checked))
        
        self.update_select_all_button()
        self.update_polygon_selectors()

        self._last_action = 'item deleted'
        self.update_status()

    # update one of item's fields
    def update_item_state(self, row, value):
        self._label_items[row].selected = value
        if value:
            self.add_polygon(row)
        else:
            self.remove_polygon(row)
        self.update_select_all_button()
        
        self._last_action = 'item selected'
        self.update_status()
        print("selected:", row)

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
    def save_label_items(self, json_path):
        weather_info = []
        if self.brightness_buttons.checkedButton():
            weather_info.append(self.brightness_buttons.checkedButton().text())
        if self.precipitation_buttons.checkedButton():
            weather_info.append(self.precipitation_buttons.checkedButton().text())
        if self.surface_buttons.checkedButton():
            weather_info.append(self.surface_buttons.checkedButton().text())
        if self.weather_buttons.checkedButton():
            weather_info.append(self.weather_buttons.checkedButton().text())

        print(f"{weather_info=}")

        data_json = {}
        data_json['objects'] = self.label_items_to_dict()
        data_json['weather'] = [w for w in weather_info if w != "none"]
        print(f"saved weather info: {data_json['weather']}")
        with open(json_path, "w") as json_file:
            json.dump(data_json, json_file, indent=4)

        self._last_action = f'json saved: {json_path}'
        self.update_status()
        
        print(f"Label items saved to {json_path}")

    # clear table, label items list and load label items from json file
    def load_label_items(self, json_path):
        try:
            with open(json_path, "r") as json_file:
                json_data = json.load(json_file)
            
            # load table items
            self._label_items.clear()
            self.table_widget.setRowCount(0)
            
            label_data = json_data['objects']
            for row, item_data in enumerate(label_data):
                print("item data:", item_data)
                name = item_data.get("name", "")
                color = item_data.get("color", "#000")
                tags = item_data.get("tags", "")
                points = item_data.get("points", [])

                self.add_item(selected=False, color=color, name=name, tags=tags, points=points)
                print(f"loading item, {color=}, {name=}, {tags=}, {points=}")

            # load weather conditions
            weather_data = json_data['weather']
            weather_options = [
                ["bright", "dark", "night"],
                ["none", "rainfall", "snowfall", "fog"],
                ['none', 'puddles', 'snow'],
                ["none", "sunny", "cloudy"]
            ]
            for g in range(3):
                self.weather_layout.itemAtPosition(1, g).widget().setChecked(True)
            for w_d in weather_data:
                for i, weather_group in enumerate(weather_options):
                    try:
                        button_id = weather_group.index(w_d)
                        self.weather_layout.itemAtPosition(button_id + 1, i).widget().setChecked(True)
                    except Exception as e:
                        pass

            self._save_path = None

            self._last_action = f'json loaded: {json_path}'
            self.update_status()
            
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
        rows = list(range(len(self._label_items)))
        for row in rows:
            self.remove_polygon(row)
        print("Removed all polygons")

    # undo last left click
    def undo_point(self):
        print("undo point")
        if self._line_plots and self._points:
            self._line_plots[-1][0].remove()
            self._line_plots.pop()
            self._points.pop()
            self._canvas.draw()

            self._last_action = 'undo point'
            self.update_status()

    # update label item's text fields
    def handle_item_changed(self, item):
        row = item.row()
        col = item.column()
        print(f"item [{row}, {col}] changed")

        if col == 3:
            self._label_items[row].name = item.text()
            self._last_action = "item's name updated"
        elif col == 4:
            self._label_items[row].tags = item.text()
            self._last_action = "item's tags updated"
        self.update_polygon_selectors()
        self.update_status()

    # handle click on checkbox cell
    def handle_cell_clicked(self, row, column):
        print(f"cell in row {row} clicked")
        if column == 2:
            self.select_color(row)

            checkbox_widget = self.table_widget.cellWidget(row, 1)
            checkbox = checkbox_widget.layout().itemAt(0).widget()
            if checkbox.isChecked():
                self.remove_polygon(row)
                self.add_polygon(row)

    def select_all_items(self):
        select_mode = True if self._select_all_button.text() == "Select all" else False
        for row in range(self.table_widget.rowCount()):
            checkbox_widget = self.table_widget.cellWidget(row, 1)
            checkbox = checkbox_widget.layout().itemAt(0).widget()
            checkbox.setChecked(select_mode)
        self.update_select_all_button()

    def update_select_all_button(self):
        all_selected = True
        for row in range(self.table_widget.rowCount()):
            checkbox_widget = self.table_widget.cellWidget(row, 1)
            checkbox = checkbox_widget.layout().itemAt(0).widget()
            if not checkbox.isChecked():
                all_selected = False
                break
        if all_selected:
            self._select_all_button.setText("Unselect all")
        else:
            self._select_all_button.setText("Select all")

    def radio_button_click(self, button):
        group = self.sender()
        group_name = ""

        if group == self.brightness_buttons:
            group_name = "brightness"
        elif group == self.precipitation_buttons:
            group_name = "precipitation"
        elif group == self.weather_buttons:
            group_name = "weather"

        self._last_action = f"{group_name} selected"
        self.update_status()
        print(f"radio button clicked: {group_name} {button.text()}")

    def plot_click(self, event):
        x, y = event.xdata, event.ydata
        print("clicked", event.button, x, y)
        if x is not None and y is not None:
            # LMB - add point to polygon
            if event.button == 1:
                if self._points:
                    self._line_plots.append(self._ax.plot([self._points[-1][0], x], [self._points[-1][1], y], 'r-'))
                    if self._point_tmp:
                        self._point_tmp[0].remove()
                        self._point_tmp = None
                else:
                    self._point_tmp = self._ax.plot(x, y, 'ro')
                self._points.append([x, y])
                self._canvas.draw()

                self._last_action = f'plot clicked ({x}, {y})'
                self.update_status()

            # wheel button
            elif event.button == 2:
                self._start_drag_x = event.xdata
                self._start_drag_y = event.ydata

            # RMB - end of sequence
            elif event.button == 3:
                self.add_item(selected=True, points=self._points)
                self._points = []
                self._line_plots = []
                self.display_image()

        # self.update_image()

    def plot_release(self, event):
        if event.button == 2:
            dx = event.xdata - self._start_drag_x
            dy = event.ydata - self._start_drag_y

            print(f"1. {self._mouse_position=}")
            cx, cy = self._center
            self._center = [cx - dx, cy - dy]
            print(f"2. {self._mouse_position=}")
            self.update_image()

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
            print(f"{type(self._image)=}")
            image_name = self._image_path
            for sep in ['\\']:
                image_name = image_name.replace(sep, '/')
            image_name = ''.join(image_name.split('/')[-1].split('.')[:-1])
            self._image_name = image_name
            
            self.display_image()
            self._save_path = None

            self._last_action = f'image loaded: {self._image_path}'
            self.update_status()

    def menu_option_load_json(self):
        print("Load Label Items option selected")
        print(f"{self._polygons=}")
        json_path = QFileDialog.getOpenFileName(self, "Load Label Items", '', "JSON files (*.json)")[0]
        if json_path:
            self.remove_all_polygons()
            self.load_label_items(json_path)

    def menu_option_save(self):
        print("Save option selected")
        json_path = ""
        if self._save_path:
            json_path = self._save_path
        else:
            json_path_initial = os.path.join(
                os.path.dirname(self._image_path), f"{self._image_name}.json"
            )

            json_path = QFileDialog.getSaveFileName(self, "Save JSON", json_path_initial, "JSON files (*.json)")[0]

        if json_path:
            self._save_path = json_path
            self.save_label_items(json_path)

    def display_image(self):
        if self._image is not None:
            self._ax.clear()
            self._ax.imshow(self._image)
            self._canvas.draw()

            self._center = [self._image.shape[0] // 2, self._image.shape[1] // 2]
            self._zoom = 1
            self.press_pos = None

            gray_image = np.dot(self._image[...,:3], [0.299, 0.587, 0.114])
            self._brightness = np.mean(gray_image)
        
        self.remove_all_polygons()
        self._polygons = {}
        for row in range(self.table_widget.rowCount()):
            checkbox_widget = self.table_widget.cellWidget(row, 1)
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
            self.table_widget.setItem(row, 2, color_item)
            self._label_items[row].color = color.name()
            
            self._last_action = 'color changed'
            self.update_status()

            print(f"Color for row {row} selected: {color.name()}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())