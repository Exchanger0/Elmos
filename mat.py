import sympy as sm
import numpy as np
import random as rand
from matplotlib.lines import Line2D


class Graph:

    __colors = ['#4242fd', '#008000', '#ff0000', '#2dbbbb', '#be08be', '#b9b93d', '#000000']

    def __init__(self, func=None, line=None, have_args=False):
        self.func = func
        self.line = line if line is not None else Line2D([], [], color=rand.choice(self.__colors))
        self.have_args = have_args

    def update(self, x_vals):
        if self.func is not None and self.line is not None:
            y_vals = self.func(x_vals) if self.have_args else [self.func()] * len(x_vals)
            self.line.set_data(x_vals, y_vals)


def delete_graph(graph, ax):
    if graph.line is not None and graph.line in ax.get_lines():
        graph.line.remove()


def plot(text_func, graph, ax):
    try:
        sympy_expr = sm.sympify(text_func)
        x_min, x_max = ax.get_xlim()

        x = sm.symbols("x")
        if x in sympy_expr.free_symbols:
            func = sm.lambdify(x, sympy_expr, "numpy")
            have_args = True
        else:
            func = sm.lambdify([], sympy_expr, "numpy")
            have_args = False

        graph.func = func
        graph.have_args = have_args
        graph.update(np.linspace(x_min, x_max, calculate_num_points(x_min, x_max)))

        if graph.line not in ax.get_lines():
            ax.add_line(graph.line)

    except Exception as e:
        print(f"Ошибка: {e}")


def update(graphs, ax):
    x_min, x_max = ax.get_xlim()

    num_points = calculate_num_points(x_min, x_max)
    x_vals = np.linspace(x_min, x_max,  num_points)
    for graph in graphs:
        graph.update(x_vals)


def calculate_num_points(x_min, x_max, base_points=1000, base_range=20):
    current_range = x_max - x_min
    zoom_factor = base_range / current_range if current_range != 0 else 1.0
    num_points = int(base_points * zoom_factor)

    num_points = max(num_points, 1000)
    num_points = min(num_points, 10000)

    return num_points