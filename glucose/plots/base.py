#!/usr/bin/env python

from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3cairo import \
    FigureCanvasGTK3Cairo as FigureCanvas


class NoPlotDataFound(Exception):
    pass


class Plot(object):

    DEFAULT_HEIGHT = 200
    DEFAULT_WIDTH = 200

    def __init__(self, height=None, width=None):
        self.figure = Figure(facecolor="white")

        if not height:
            self.height = self.DEFAULT_HEIGHT
        if not width:
            self.width = self.DEFAULT_WIDTH

    def get_canvas(self):
        self.render()
        canvas = FigureCanvas(self.figure)
        canvas.set_size_request(self.height, self.width)
        return canvas
