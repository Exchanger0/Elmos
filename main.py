import sys

import numpy as np
import sympy as sm
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, \
    QWidget, QLineEdit, QHBoxLayout, QScrollArea
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from matplotlib.lines import Line2D


class CustomSettingsWindow(QWidget):
    def __init__(self, ax, canvas):
        super().__init__()
        self.ax = ax
        self.canvas = canvas
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Настройки графика')
        self.setGeometry(600, 400, 300, 200)

        layout = QVBoxLayout()

        xmin, xmax = self.ax.get_xlim()
        ymin, ymax = self.ax.get_ylim()

        # Поля для настройки осей X и Y
        self.xmin_input = QLineEdit(self)
        self.xmin_input.setText(str(xmin))
        layout.addWidget(QLabel("Минимум X:"))
        layout.addWidget(self.xmin_input)

        self.xmax_input = QLineEdit(self)
        self.xmax_input.setText(str(xmax))
        layout.addWidget(QLabel("Максимум X:"))
        layout.addWidget(self.xmax_input)

        self.ymin_input = QLineEdit(self)
        self.ymin_input.setText(str(ymin))
        layout.addWidget(QLabel("Минимум Y:"))
        layout.addWidget(self.ymin_input)

        self.ymax_input = QLineEdit(self)
        self.ymax_input.setText(str(ymax))
        layout.addWidget(QLabel("Максимум Y:"))
        layout.addWidget(self.ymax_input)

        # Кнопка применения настроек
        self.apply_button = QPushButton('Применить', self)
        self.apply_button.clicked.connect(self.apply_settings)
        layout.addWidget(self.apply_button)

        self.setLayout(layout)

    def apply_settings(self):
        try:
            # Устанавливаем новые лимиты осей
            xmin = float(self.xmin_input.text())
            xmax = float(self.xmax_input.text())
            ymin = float(self.ymin_input.text())
            ymax = float(self.ymax_input.text())

            self.ax.set_xlim([xmin, xmax])
            self.ax.set_ylim([ymin, ymax])

            # Обновляем график
            self.canvas.draw()
        except ValueError:
            print("Ошибка: введите корректные числовые значения")


class Graph:

    def __init__(self, func=None, line=None, have_args=False):
        self.func = func
        self.line = line if line is not None else Line2D([], [])
        self.have_args = have_args

    def update(self, x_vals):
        if self.func is not None and self.line is not None:
            y_vals = self.func(x_vals) if self.have_args else [self.func()] * len(x_vals)
            self.line.set_data(x_vals, y_vals)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.scale_factor = 1
        self.graphs = []
        self.input_graphs = {}

        self.setWindowTitle("Desmos")
        self.setGeometry(100, 100, 1200, 800)

        self.mwidget = QWidget()
        self.setCentralWidget(self.mwidget)

        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.mpl_connect("scroll_event", self.on_scroll)

        self.ax = self.figure.add_subplot()
        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)
        self.ax.grid(True)
        self.figure.canvas.mpl_connect('draw_event', lambda event: self.redraw())

        self.navbar = NavigationToolbar2QT(self.canvas, self)

        actions = self.navbar.actions()
        delete_actions = ["Back", "Forward", "Zoom", "Subplots"]
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
            elif action.text() == "Customize":
                action.setToolTip("Настройки графика")
                action.triggered.disconnect()
                action.triggered.connect(self.open_settings)

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

    def open_settings(self):
        # Открываем окно настроек
        self.settings_window = CustomSettingsWindow(self.ax, self.canvas)
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
        label = QLabel("y =")
        text = QLineEdit()
        text.setPlaceholderText("Введите уравнение")
        lay1.addWidget(label)
        lay1.addWidget(text)

        draw_btn = QPushButton("Draw")
        draw_btn.clicked.connect(lambda: self.plot(text.text(), self.input_graphs[parent]))

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(lambda: self.delete_graph(parent, self.input_graphs[parent]))
        # delete_btn.clicked.connect(lambda: self.scroll_layout.removeWidget(parent))

        lay2 = QHBoxLayout()
        lay2.setSpacing(5)
        lay2.setContentsMargins(0, 0, 0, 0)
        lay2.addWidget(draw_btn)
        lay2.addWidget(delete_btn)

        main_lay.addLayout(lay1)
        main_lay.addLayout(lay2)
        self.input_graphs[parent] = Graph()

        self.scroll_layout.addWidget(parent)

    def delete_graph(self, parent, graph: Graph):
        print("hello")
        try:
            print(parent in self.input_graphs)
            if parent in self.input_graphs:
                del self.input_graphs[parent]
            self.scroll_layout.removeWidget(parent)
            parent.deleteLater()
            if graph.line is not None:
                if graph.line in self.ax.get_lines():
                    graph.line.remove()
                    self.canvas.draw()
            print(1)
        except Exception as e:
            print("Error:", e)

    @staticmethod
    def calculate_num_points(x_min, x_max, base_points=1000, base_range=20):
        current_range = x_max - x_min
        zoom_factor = base_range / current_range if current_range != 0 else 1.0
        num_points = int(base_points * zoom_factor)

        num_points = max(num_points, 1000)
        num_points = min(num_points, 10000)

        return num_points

    def plot(self, text_func: str, graph: Graph):
        try:
            sympy_expr = sm.sympify(text_func)
            x_min, x_max = self.ax.get_xlim()
            x = sm.symbols("x")
            if x in sympy_expr.free_symbols:
                func = sm.lambdify(x, sympy_expr, "numpy")
                have_args = True
            else:
                func = sm.lambdify([], sympy_expr, "numpy")
                have_args = False

            graph.func = func
            graph.have_args = have_args
            graph.update(np.linspace(x_min, x_max, self.calculate_num_points(x_min, x_max)))

            if graph.line not in self.ax.get_lines():
                self.ax.add_line(graph.line)

            self.canvas.draw()

        except Exception as e:
            print(f"Ошибка: {e}")

    def redraw(self):
        x_min, x_max = self.ax.get_xlim()

        num_points = self.calculate_num_points(x_min, x_max)
        x_vals = np.linspace(x_min, x_max,  num_points)
        print("points:", num_points)
        for graph in self.input_graphs.values():
            graph.update(x_vals)

    def home(self):
        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)
        self.canvas.draw()

    def on_scroll(self, event):
        # get the current x and y limits
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        cur_xrange = (cur_xlim[1] - cur_xlim[0]) / 2
        cur_yrange = (cur_ylim[1] - cur_ylim[0]) / 2
        center_x = (cur_xlim[0] + cur_xlim[1]) / 2
        center_y = (cur_ylim[0] + cur_ylim[1]) / 2
        base_scale = 1.05
        if event.button == 'up':
            # deal with zoom in
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            # deal with zoom out
            scale_factor = base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1
        self.scale_factor = scale_factor
        # set new limits
        self.ax.set_xlim([center_x - cur_xrange * scale_factor,
                          center_x + cur_xrange * scale_factor])
        self.ax.set_ylim([center_y - cur_yrange * scale_factor,
                          center_y + cur_yrange * scale_factor])

        self.redraw()
        self.canvas.draw()


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()
