import inspect
import re
import traceback
from enum import Enum
from abc import ABC, abstractmethod
from typing import Callable

import sympy as sm
import numpy as np
import random as rand

from matplotlib.axes import Axes
from matplotlib.lines import Line2D


def logb(x, b):
    return np.log(x) / np.log(b)


def custom_pow(base, exp):
    return base ** exp


modules = ["numpy", {"logb": logb, "^": custom_pow}]

class GraphType(Enum):
    X = "x"
    Y = "y"
    POINTS = "points"


class DynamicRange:
    def __init__(self, _min: float | None, min_is_dynamic: bool, _max: float | None, max_is_dynamic: bool):
        self.min = _min
        self.min_is_dynamic = min_is_dynamic
        self.max = _max
        self.max_is_dynamic = max_is_dynamic

    def in_range(self, num: float):
        if self.min is None and self.max is None:
            return True
        elif self.min is None and self.max is not None:
            return num <= self.max
        elif self.min is not None and self.max is None:
            return num >= self.min
        else:
            return self.min <= num <= self.max


class AbstractGraph(ABC):
    __colors = ['#4242fd', '#008000', '#ff0000', '#2dbbbb', '#be08be', '#b9b93d', '#000000']
    graph_type: GraphType
    line: Line2D

    def __init__(self, graph_type: GraphType):
        super().__init__()
        self.graph_type = graph_type
        self.line = Line2D([], [], color=rand.choice(self.__colors))

    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def process_text(self, text: str):
        pass


class LimGraph(AbstractGraph, ABC):

    def __init__(self, graph_type: GraphType, lim_x: DynamicRange | None, lim_y: DynamicRange | None ):
        super().__init__(graph_type)
        self.lim_x = lim_x if lim_x is not None else DynamicRange(None, True, None, True)
        self.lim_y = lim_y if lim_y is not None else DynamicRange(None, True, None, True)

    def update_lim_x(self, _min: float, _max: float):
        if self.lim_x.min_is_dynamic:
            self.lim_x.min = _min
        if self.lim_x.max_is_dynamic:
            self.lim_x.max = _max

    def update_lim_y(self, _min: float, _max: float):
        if self.lim_y.min_is_dynamic:
            self.lim_y.min = _min
        if self.lim_y.max_is_dynamic:
            self.lim_y.max = _max


class FuncGraph(LimGraph, ABC):
    def __init__(self, graph_type: GraphType, func: Callable = None, lim_x: DynamicRange = None, lim_y: DynamicRange = None):
        super().__init__(graph_type, lim_x, lim_y)
        self.func = func

    @property
    def func(self):
        return self.__func

    @func.setter
    def func(self, func: Callable):
        self.__func = func
        if func is not None:
            self._have_arg = len(inspect.signature(func).parameters.keys()) != 0
        else:
            self._have_arg = False


class GraphY(FuncGraph):
    def __init__(self, func: Callable = None, lim_x: DynamicRange = None, lim_y: DynamicRange = None):
        super().__init__(GraphType.Y, func, lim_x, lim_y)

    def draw(self):
        try:
            if self.func is not None:
                num_points = calculate_num_points(self.lim_x.min, self.lim_x.max)
                x_vals = np.linspace(self.lim_x.min, self.lim_x.max, num_points)
                y_vals = self.func(x_vals) if self._have_arg else [self.func()] * len(x_vals)
                y_vals = np.where([self.lim_y.in_range(y) for y in y_vals], y_vals, np.nan)
                self.line.set_data(x_vals, y_vals)
        except Exception as e:
            pass

    def process_text(self, text: str):
        try:
            sympy_expr = sm.sympify(text)
            x = sm.symbols("x")
            if x in sympy_expr.free_symbols:
                self.func = sm.lambdify(x, sympy_expr, modules)
            else:
                self.func = sm.lambdify([], sympy_expr, modules)
        except Exception as e:
            traceback.print_exception(e)


class GraphX(FuncGraph):

    def __init__(self, func: Callable = None, lim_x: DynamicRange = None, lim_y: DynamicRange = None):
        super().__init__(GraphType.X, func, lim_x, lim_y)

    def draw(self):
        try:
            if self.func is not None:
                num_points = calculate_num_points(self.lim_y.min, self.lim_y.max)
                y_vals = np.linspace(self.lim_y.min, self.lim_y.max, num_points)
                x_vals = self.func(y_vals) if self._have_arg else [self.func()] * len(y_vals)
                x_vals = np.where([self.lim_x.in_range(x) for x in x_vals], x_vals, np.nan)
                self.line.set_data(x_vals, y_vals)
        except:
            pass

    def process_text(self, text: str):
        sympy_expr = sm.sympify(text)
        y = sm.symbols("y")
        if y in sympy_expr.free_symbols:
            self.func = sm.lambdify(y, sympy_expr, modules)
        else:
            self.func = sm.lambdify([], sympy_expr, modules)


class GraphPoints(AbstractGraph):

    def __init__(self, points: list[tuple[float, float]]):
        super().__init__(GraphType.POINTS)
        self.__x_points = []
        self.__y_points = []
        self.set_points(points)

    def set_points(self, points: list[tuple[float, float]]):
        self.__x_points.clear()
        self.__y_points.clear()
        for x, y in points:
            self.add_point(x, y)

    def add_point(self, x, y):
        self.__x_points.append(x)
        self.__y_points.append(y)

    def draw(self):
        self.line.set_data(self.__x_points, self.__y_points)

    def process_text(self, text: str):
        points = []
        for gr in re.finditer(r"(\(-?[0-9]+;-?[0-9]+\))", text.replace(" ", "")):
            g = gr.group()
            x = int(g[g.index("(") + 1:g.index(";")])
            y = int(g[g.index(";") + 1:g.index(")")])
            points.append((x, y))
        self.set_points(points)


def delete_graph(graph: AbstractGraph, ax: Axes):
    if graph.line is not None and graph.line in ax.get_lines():
        graph.line.remove()


def plot(text_func: str, graph: AbstractGraph, ax: Axes):
    if isinstance(graph, LimGraph):
        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()
        graph.update_lim_x(x_min, x_max)
        graph.update_lim_y(y_min, y_max)

    graph.process_text(text_func)
    graph.draw()

    if graph.line not in ax.get_lines():
        ax.add_line(graph.line)


def calculate_num_points(val_min, val_max, base_range=20):
    min_points = 5000
    max_points = 30_000
    eps = 1e-6
    current_range = max(abs(val_max - val_min), eps)

    sigmoid_factor = 1 / (1 + np.exp(0.1 * (current_range - base_range)))

    num_points = int((max_points - min_points) * sigmoid_factor + min_points)

    return num_points
