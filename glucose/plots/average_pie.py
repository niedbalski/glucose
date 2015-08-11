#!/usr/bin/env python

from glucose.plots.base import Plot
from glucose.model import Reading
from glucose.helpers import format_as_percent


class AverageReadings(Plot):

    title = "Average Glucose Readings"

    def __init__(self, from_date=None):
        Plot.__init__(self)

        (total, low, normal, high) = self.get_data(from_date=from_date)

        ax = self.figure.add_subplot(111, aspect='equal', axisbg="white")
        ax.set_axis_bgcolor('red')

        ax.pie([low, high, normal],
               labels=[format_as_percent(low, total, 'Lows {}',
                                         low),
                       format_as_percent(high, total, 'Highs {}',
                                         high),
                       format_as_percent(normal,
                                         total, 'Normal {}',
                                         normal)],

               colors=['orange', 'red', 'green'], shadow=True,
               explode=(0, 0, 0.2))

        ax.set_title(self.title)
        ax.plot()

        self.ax = ax

    def refresh(self, from_date=None):
        (total, low, normal, high) = self.get_data(from_date=from_date)

        self.ax.clear()
        self.ax.pie([low, high, normal],
                    labels=[format_as_percent(low, total, 'Lows {}',
                                              low),
                            format_as_percent(high, total, 'Highs {}',
                                              high),
                            format_as_percent(normal,
                                              total, 'Normal {}',
                                              normal)],

                    colors=['orange', 'red', 'green'], shadow=True,
                    explode=(0, 0, 0.2))

        self.ax.set_title(self.title)
        self.figure.canvas.draw_idle()

    def get_data(self, from_date=None):
        return Reading.group_by_range(from_date=from_date)
