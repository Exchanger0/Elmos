import re

from matplotlib.axes import Axes

import mat
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QHBoxLayout, QColorDialog, \
    QMainWindow, QScrollArea, QCheckBox, QButtonGroup, QMessageBox, QComboBox
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class ChangeLimWidget(QWidget):
    def __init__(self, title: str, lim: mat.DynamicRange):
        super().__init__()

        self.lim = lim

        min_group = QButtonGroup(self)
        min_group.setExclusive(True)

        self.min_label = QLabel(f"Min {title}", self)
        self.min_checkbox1 = QCheckBox("Динамически", self)
        self.min_checkbox1.setTristate(False)
        self.min_checkbox2 = QCheckBox("Установить самому", self)
        self.min_checkbox2.setTristate(False)
        self.min_text_field = QLineEdit(self)
        self.min_text_field.setVisible(False)
        self.min_checkbox2.stateChanged.connect(self.min_toggle_text_field)

        min_group.addButton(self.min_checkbox1)
        min_group.addButton(self.min_checkbox2)

        if not lim.min_is_dynamic:
            self.min_checkbox2.setChecked(True)
            self.min_text_field.setText(str(lim.min))
        else:
            self.min_checkbox1.setChecked(True)

        max_group = QButtonGroup(self)
        max_group.setExclusive(True)

        self.max_label = QLabel(f"Max {title}", self)
        self.max_checkbox1 = QCheckBox("Динамически", self)
        self.max_checkbox1.setTristate(False)
        self.max_checkbox2 = QCheckBox("Установить самому", self)
        self.max_checkbox2.setTristate(False)
        self.max_text_field = QLineEdit(self)
        self.max_text_field.setVisible(False)
        self.max_checkbox2.stateChanged.connect(self.max_toggle_text_field)

        max_group.addButton(self.max_checkbox1)
        max_group.addButton(self.max_checkbox2)

        if not lim.max_is_dynamic:
            self.max_checkbox2.setChecked(True)
            self.max_text_field.setText(str(lim.max))
        else:
            self.max_checkbox1.setChecked(True)

        min_layout = QVBoxLayout()
        min_layout.addWidget(self.min_label)
        min_layout.addWidget(self.min_checkbox1)
        min_layout.addWidget(self.min_checkbox2)
        min_layout.addWidget(self.min_text_field)

        max_layout = QVBoxLayout()
        max_layout.addWidget(self.max_label)
        max_layout.addWidget(self.max_checkbox1)
        max_layout.addWidget(self.max_checkbox2)
        max_layout.addWidget(self.max_text_field)

        main_lay = QHBoxLayout()
        main_lay.addLayout(min_layout)
        main_lay.addLayout(max_layout)
        self.setLayout(main_lay)

    def min_toggle_text_field(self, state):
        self.min_text_field.setVisible(state == 2)

    def max_toggle_text_field(self, state):
        self.max_text_field.setVisible(state == 2)

    def apply_settings(self):
        if self.min_checkbox2.isChecked() and re.fullmatch(r"-?\d+\.?\d*", self.min_text_field.text().strip()):
            self.lim.min_is_dynamic = self.min_checkbox1.isChecked()
            self.lim.min = float(self.min_text_field.text().strip())
        elif self.min_checkbox1.isChecked():
            self.lim.min_is_dynamic = True

        if self.max_checkbox2.isChecked() and re.fullmatch(r"-?\d+\.?\d*", self.max_text_field.text().strip()):
            self.lim.max_is_dynamic = self.max_checkbox1.isChecked()
            self.lim.max = float(self.max_text_field.text().strip())
        elif self.max_checkbox1.isChecked():
            self.lim.max_is_dynamic = True


class CustomizeLineWindow(QWidget):
    def __init__(self, graph: mat.AbstractGraph, canvas, ax: Axes):
        super().__init__()
        self.graph = graph
        self.canvas = canvas
        self.ax = ax
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Настройки графика')
        self.setGeometry(600, 400, 300, 200)

        layout = QVBoxLayout()

        self.color = self.graph.line.get_color()
        self.color_label = QLabel(f"Выбранный цвет: {self.graph.line.get_color()}")
        self.color_label.setStyleSheet(f"background-color: {self.graph.line.get_color()}; color: white;")

        self.color_button = QPushButton("Выбрать цвет")
        self.color_button.clicked.connect(self.pick_color)

        self.title_label = QLabel("Метка:")
        label = self.graph.line.get_label()
        self.title_field = QLineEdit("" if not label or label[0] == "_" else label)
        lay = QHBoxLayout()
        lay.addWidget(self.title_label)
        lay.addWidget(self.title_field)

        self.apply_button = QPushButton('Применить', self)
        self.apply_button.clicked.connect(self.apply_settings)

        layout.addWidget(self.color_label)
        layout.addWidget(self.color_button)
        layout.addLayout(lay)

        if isinstance(self.graph, mat.LimGraph):
            self.lim_x_widget = ChangeLimWidget("x", self.graph.lim_x)
            self.lim_y_widget = ChangeLimWidget("y", self.graph.lim_y)
            layout.addWidget(self.lim_x_widget)
            layout.addWidget(self.lim_y_widget)

        layout.addWidget(self.apply_button)
        self.setLayout(layout)

    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color = color.name()
            self.color_label.setText(f"Выбранный цвет: {self.color}")
            self.color_label.setStyleSheet(f"background-color: {self.color}; color: white;")

    def apply_settings(self):
        self.graph.line.set_color(self.color)
        self.graph.line.set_label(self.title_field.text().replace("_", ""))
        if isinstance(self.graph, mat.LimGraph):
            self.lim_x_widget.apply_settings()
            self.lim_y_widget.apply_settings()
        self.ax.legend()
        self.canvas.draw()


class RedrawCanvas(FigureCanvasQTAgg):

    def __init__(self, figure=None, main_w=None):
        super().__init__(figure)
        self.main_v = main_w

    def draw(self, *args, **kwargs):
        self.main_v.redraw()
        super().draw()


class InputFuncWindget(QWidget):
    def __init__(self, parent, graph_type: mat.GraphType, ax: Axes, canvas):
        super().__init__(parent)
        parent.layout().addWidget(self)
        self.graph_type = graph_type
        self.ax = ax
        self.canvas = canvas
        match graph_type:
            case mat.GraphType.X:
                self.graph = mat.GraphX()
            case mat.GraphType.Y:
                self.graph = mat.GraphY()
            case mat.GraphType.POINTS:
                self.graph = mat.GraphPoints([])

        self.setMaximumHeight(130)
        main_lay = QVBoxLayout()
        main_lay.setSpacing(0)
        main_lay.setContentsMargins(10, 10, 10, 10)
        self.setLayout(main_lay)

        lay1 = QHBoxLayout()
        lay1.setSpacing(0)
        lay1.setContentsMargins(0, 0, 0, 0)
        label = QLabel(self.graph_type.value + " = ")
        self.text = QLineEdit()
        self.text.setPlaceholderText("Введите уравнение")
        lay1.addWidget(label)
        lay1.addWidget(self.text)

        draw_btn = QPushButton("Нарисовать")
        draw_btn.clicked.connect(self.draw)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self.delete_graph)

        customize_btn = QPushButton("Параметры")
        customize_btn.clicked.connect(self.open_settings)

        lay2 = QHBoxLayout()
        lay2.setSpacing(5)
        lay2.setContentsMargins(0, 0, 0, 0)
        lay2.addWidget(draw_btn)
        lay2.addWidget(delete_btn)
        lay2.addWidget(customize_btn)

        main_lay.addLayout(lay1)
        main_lay.addLayout(lay2)

    def draw(self):
        try:
            mat.plot(self.text.text(), self.graph, self.ax)
            self.canvas.draw()
        except Exception as e:
            QMessageBox.warning(self, "Error", "Wrong function")

    def delete_graph(self):
        self.parent().layout().removeWidget(self)
        self.deleteLater()

        mat.delete_graph(self.graph, self.ax)

        if len(self.ax.get_legend_handles_labels()[0]) == 0:
            self.ax.legend_ = None
        else:
            self.ax.legend()

        self.canvas.draw()

    def open_settings(self):
        self.settings_window = CustomizeLineWindow(self.graph, self.canvas, self.ax)
        self.settings_window.show()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.input_func_widgets: list[InputFuncWindget] = []

        self.setWindowTitle("Elmos")
        self.setGeometry(100, 100, 1200, 800)

        self.mwidget = QWidget()
        self.setCentralWidget(self.mwidget)

        self.figure = Figure()
        self.canvas = RedrawCanvas(self.figure, self)
        self.canvas.mpl_connect("scroll_event", self.on_scroll)

        self.ax = self.figure.add_subplot()
        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)
        self.ax.grid(True)

        self.navbar = NavigationToolbar2QT(self.canvas, self)

        actions = self.navbar.actions()
        delete_actions = ["Back", "Forward", "Zoom", "Subplots", "Customize"]
        for action in actions:
            if action.text() in delete_actions:
                self.navbar.removeAction(action)

            if action.text() == "Home":
                action.triggered.connect(self.home)
                action.setToolTip("Восстанавливает исходный вид")
            elif action.text() == "Save":
                action.setToolTip("Сохранить график")
            elif action.text() == "Pan":
                action.setToolTip("Перемещать график")

        self.gtypes = QComboBox()
        self.gtypes.addItems(["y", "x", "points"])
        self.add_input_field_btn = QPushButton("+")
        self.add_input_field_btn.clicked.connect(lambda: self.add_input_field(self.gtypes.currentText()))
        gt_if_lay = QHBoxLayout()
        gt_if_lay.addWidget(self.add_input_field_btn)
        gt_if_lay.addWidget(self.gtypes)
        gt_if_lay.setStretch(0, 2)
        gt_if_lay.setStretch(1, 1)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(20)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_content)

        self.lay = QVBoxLayout(self.mwidget)
        self.lay.addWidget(self.canvas)
        self.lay.addWidget(self.navbar)
        self.lay.addLayout(gt_if_lay)
        self.lay.addWidget(self.scroll_area)

    def add_input_field(self, graph_type: str):
        match graph_type.lower():
            case "x":
                self.input_func_widgets.append(
                    InputFuncWindget(self.scroll_content, mat.GraphType.X, self.ax, self.canvas)
                )
            case "y":
                self.input_func_widgets.append(
                    InputFuncWindget(self.scroll_content, mat.GraphType.Y, self.ax, self.canvas)
                )
            case "points":
                self.input_func_widgets.append(
                    InputFuncWindget(self.scroll_content, mat.GraphType.POINTS, self.ax, self.canvas)
                )

    def home(self):
        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)
        self.canvas.draw()

    def redraw(self, *args):
        for ifw in self.input_func_widgets:
            if isinstance(ifw.graph, mat.LimGraph):
                x_min, x_max = self.ax.get_xlim()
                y_min, y_max = self.ax.get_ylim()
                ifw.graph.update_lim_x(x_min, x_max)
                ifw.graph.update_lim_y(y_min, y_max)
            ifw.graph.draw()

    def on_scroll(self, event):
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        cur_xrange = (cur_xlim[1] - cur_xlim[0]) / 2
        cur_yrange = (cur_ylim[1] - cur_ylim[0]) / 2
        center_x = (cur_xlim[0] + cur_xlim[1]) / 2
        center_y = (cur_ylim[0] + cur_ylim[1]) / 2
        base_scale = 1.1
        if event.button == 'up':
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            scale_factor = base_scale
        else:
            scale_factor = 1
        self.scale_factor = scale_factor
        self.ax.set_xlim([center_x - cur_xrange * scale_factor,
                          center_x + cur_xrange * scale_factor])
        self.ax.set_ylim([center_y - cur_yrange * scale_factor,
                          center_y + cur_yrange * scale_factor])

        self.canvas.draw()
