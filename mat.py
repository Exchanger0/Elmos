import sympy as sm
import numpy as np
import random as rand
from matplotlib.lines import Line2D


class Graph:
    __colors = ['#4242fd', '#008000', '#ff0000', '#2dbbbb', '#be08be', '#b9b93d', '#000000']

    class Lim:
        def __init__(self, value, is_dynamic):
            super().__init__()
            self.value = value
            self.is_dynamic = is_dynamic

        def __repr__(self):
            return f"Lim(value={self.value} is_dynamic={self.is_dynamic})"

    def __init__(self, func=None, line=None, have_args=False, x_min=None, x_max=None, y_min=None, y_max=None, gtype="x"):
        self.func = func
        self.line = line if line is not None else Line2D([], [], color=rand.choice(self.__colors))
        self.have_args = have_args
        self.x_min = Graph.Lim(x_min, True)
        self.x_max = Graph.Lim(x_max, True)
        self.y_min = Graph.Lim(y_min, True)
        self.y_max = Graph.Lim(y_max, True)
        self.gtype = gtype.lower()

    def update(self):
        try:
            if self.func is not None and self.line is not None:
                if self.gtype == "y":
                    num_points = calculate_num_points(self.x_min.value, self.x_max.value)
                    x_vals = np.linspace(self.x_min.value, self.x_max.value, num_points)
                    y_vals = self.func(x_vals) if self.have_args else [self.func()] * len(x_vals)
                    y_vals = np.where((y_vals >= self.y_min.value) & (y_vals <= self.y_max.value), y_vals, np.nan)
                    self.line.set_data(x_vals, y_vals)
                elif self.gtype == "x":
                    num_points = calculate_num_points(self.y_min.value, self.y_max.value)
                    y_vals = np.linspace(self.y_min.value, self.y_max.value, num_points)
                    x_vals = self.func(y_vals) if self.have_args else [self.func()] * len(y_vals)
                    x_vals = np.where((x_vals >= self.x_min.value) & (x_vals <= self.x_max.value), x_vals, np.nan)
                    self.line.set_data(x_vals, y_vals)
        except Exception:
            self.func = None
            self.line.set_data([], [])
            raise Exception("Wrong function")


def delete_graph(graph, ax):
    if graph.line is not None and graph.line in ax.get_lines():
        graph.line.remove()


def plot(text_func, graph, ax, gtype):
    sympy_expr = sm.sympify(text_func)
    if gtype.lower() == "x":
        val = sm.symbols("y")
    elif gtype.lower() == "y":
        val = sm.symbols("x")
    else:
        return

    if val in sympy_expr.free_symbols:
        func = sm.lambdify(val, sympy_expr, "numpy")
        have_args = True
    else:
        func = sm.lambdify([], sympy_expr, "numpy")
        have_args = False

    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    graph.func = func
    graph.have_args = have_args
    graph.gtype = gtype
    if graph.x_min.is_dynamic:
        graph.x_min.value = x_min
    if graph.x_max.is_dynamic:
        graph.x_max.value = x_max
    if graph.y_min.is_dynamic:
        graph.y_min.value = y_min
    if graph.y_max.is_dynamic:
        graph.y_max.value = y_max
    graph.update()

    if graph.line not in ax.get_lines():
        ax.add_line(graph.line)


def calculate_num_points(val_min, val_max, base_range=20):
    min_points = 10000
    max_points = 50_000
    eps = 1e-6
    current_range = max(abs(val_max - val_min), eps)

    sigmoid_factor = 1 / (1 + np.exp(0.1 * (current_range - base_range)))

    num_points = int((max_points - min_points) * sigmoid_factor + min_points)

    return num_points
