#!/usr/bin/env python

from glucose.plots.base import Plot, NoPlotDataFound
from glucose.model import Reading
from glucose.helpers import format_as_percent


class AverageReadings(Plot):

    title = "Average Glucose Readings"

    def __init__(self, *args, **kwargs):
        Plot.__init__(self, *args, **kwargs)

        (total, low, normal, high) = self.get_data()

        if not total:
            raise NoPlotDataFound()

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

    def refresh(self):
        (total, low, normal, high) = self.get_data()

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

    def get_data(self):
        return Reading.group_by_range()
