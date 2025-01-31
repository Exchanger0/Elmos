import re

import mat
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QHBoxLayout, QColorDialog, \
    QMainWindow, QScrollArea, QCheckBox, QButtonGroup
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class ChangeLimWidget(QWidget):
    def __init__(self, title, lim: mat.Graph.Lim):
        super().__init__()

        self.lim = lim

        group = QButtonGroup(self)
        group.setExclusive(True)

        self.label = QLabel(title, self)
        self.checkbox1 = QCheckBox("Динамически", self)
        self.checkbox1.setTristate(False)
        self.checkbox2 = QCheckBox("Установить самому", self)
        self.checkbox2.setTristate(False)
        self.text_field = QLineEdit(self)
        self.text_field.setVisible(False)

        self.checkbox2.stateChanged.connect(self.toggle_text_field)

        group.addButton(self.checkbox1)
        group.addButton(self.checkbox2)

        if not lim.is_dynamic:
            self.checkbox2.setChecked(True)
            self.text_field.setText(str(lim.value))
        else:
            self.checkbox1.setChecked(True)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.checkbox1)
        layout.addWidget(self.checkbox2)
        layout.addWidget(self.text_field)

        self.setLayout(layout)

    def toggle_text_field(self, state):
        self.text_field.setVisible(state == 2)

    def apply_settings(self):
        if self.checkbox2.isChecked() and re.fullmatch(r"-?\d+\.?\d*", self.text_field.text().strip()):
            self.lim.is_dynamic = self.checkbox1.isChecked()
            self.lim.value = float(self.text_field.text().strip())
        elif self.checkbox1.isChecked():
            self.lim.is_dynamic = True


class CustomizeLineWindow(QWidget):
    def __init__(self, graph, canvas, ax):
        super().__init__()
        self.graph = graph
        self.canvas = canvas
        self.ax = ax
        self.initUI()

    def initUI(self):
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

        self.xmin_widget = ChangeLimWidget("X min", self.graph.x_min)
        self.xmax_widget = ChangeLimWidget("X max", self.graph.x_max)
        xlim_lay = QHBoxLayout()
        xlim_lay.setSpacing(10)
        xlim_lay.addWidget(self.xmin_widget)
        xlim_lay.addWidget(self.xmax_widget)

        self.ymin_widget = ChangeLimWidget("Y min", self.graph.y_min)
        self.ymax_widget = ChangeLimWidget("Y max", self.graph.y_max)
        ylim_lay = QHBoxLayout()
        ylim_lay.setSpacing(10)
        ylim_lay.addWidget(self.ymin_widget)
        ylim_lay.addWidget(self.ymax_widget)

        self.apply_button = QPushButton('Применить', self)
        self.apply_button.clicked.connect(self.apply_settings)

        layout.addWidget(self.color_label)
        layout.addWidget(self.color_button)
        layout.addLayout(lay)
        layout.addLayout(xlim_lay)
        layout.addLayout(ylim_lay)
        # layout.addWidget(self.xmin_widget)
        # layout.addWidget(self.xmax_widget)
        # layout.addWidget(self.ymin_widget)
        # layout.addWidget(self.ymax_widget)
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
        self.xmin_widget.apply_settings()
        self.xmax_widget.apply_settings()
        self.ymin_widget.apply_settings()
        self.ymax_widget.apply_settings()
        self.ax.legend()
        self.canvas.draw()


class RedrawCanvas(FigureCanvasQTAgg):

    def __init__(self, figure=None, main_w=None):
        super().__init__(figure)
        self.main_v = main_w

    def draw(self, *args, **kwargs):
        self.main_v.redraw()
        super().draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.widget_to_graph = {}

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

        self.add_input_field_btn = QPushButton("+")
        self.add_input_field_btn.clicked.connect(self.add_input_field)

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
        self.lay.addWidget(self.add_input_field_btn)
        self.lay.addWidget(self.scroll_area)

    def open_settings(self, graph):
        self.settings_window = CustomizeLineWindow(graph, self.canvas, self.ax)
        self.settings_window.show()

    def add_input_field(self):
        parent = QWidget()
        parent.setMaximumHeight(130)
        main_lay = QVBoxLayout()
        main_lay.setSpacing(0)
        main_lay.setContentsMargins(10, 10, 10, 10)
        parent.setLayout(main_lay)

        lay1 = QHBoxLayout()
        lay1.setSpacing(0)
        lay1.setContentsMargins(0, 0, 0, 0)
        label = QLabel("y = ")
        text = QLineEdit()
        text.setPlaceholderText("Введите уравнение")
        lay1.addWidget(label)
        lay1.addWidget(text)

        draw_btn = QPushButton("Нарисовать")
        draw_btn.clicked.connect(lambda: self.draw(text.text(), self.widget_to_graph[parent]))

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(lambda: self.delete_graph(parent, self.widget_to_graph[parent]))

        customize_btn = QPushButton("Параметры")
        customize_btn.clicked.connect(lambda: self.open_settings(self.widget_to_graph[parent]))

        lay2 = QHBoxLayout()
        lay2.setSpacing(5)
        lay2.setContentsMargins(0, 0, 0, 0)
        lay2.addWidget(draw_btn)
        lay2.addWidget(delete_btn)
        lay2.addWidget(customize_btn)

        main_lay.addLayout(lay1)
        main_lay.addLayout(lay2)
        self.widget_to_graph[parent] = mat.Graph()

        self.scroll_layout.addWidget(parent)

    def home(self):
        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)
        self.canvas.draw()

    def draw(self, text, graph):
        mat.plot(text, graph, self.ax)
        self.canvas.draw()

    def redraw(self, *args):
        for graph in self.widget_to_graph.values():
            x_min, x_max = self.ax.get_xlim()
            y_min, y_max = self.ax.get_ylim()
            if graph.x_min.is_dynamic:
                graph.x_min.value = x_min
            if graph.x_max.is_dynamic:
                graph.x_max.value = x_max
            if graph.y_min.is_dynamic:
                graph.y_min.value = y_min
            if graph.y_max.is_dynamic:
                graph.y_max.value = y_max
            graph.update()

    def delete_graph(self, parent, graph):
        del self.widget_to_graph[parent]
        self.scroll_layout.removeWidget(parent)
        parent.deleteLater()

        mat.delete_graph(graph, self.ax)

        if len(self.ax.get_legend_handles_labels()[0]) == 0:
            self.ax.legend_ = None
        else:
            self.ax.legend()

        self.canvas.draw()

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
