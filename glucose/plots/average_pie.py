#!/usr/bin/env python

from glucose.plots.base import Plot, NoPlotDataFound
from glucose.model import Reading
from glucose.helpers import format_as_percent


class AverageReadings(Plot):

    title = "Average Glucose Readings"

    def __init__(self, *args, **kwargs):
        Plot.__init__(self, *args, **kwargs)

    def render(self):
        (total, low, normal, high) = Reading.group_by_range()

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
