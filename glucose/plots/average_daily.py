#!/usr/bin/env python

from glucose.plots.base import Plot, NoPlotDataFound
from glucose.model import Reading

from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt

import datetime


class AverageReadingsDaily(Plot):

    title = "Average Glucose Readings Daily"

    def __init__(self, *args, **kwargs):
        Plot.__init__(self, *args, **kwargs)

    def render(self):
        grouped_readings = Reading.group_by_day()

        values = [x.avg for x in grouped_readings]
        days = [datetime.datetime.strptime(
            y.day, '%Y-%m-%d') for y in grouped_readings]

        if not values:
            raise NoPlotDataFound()

        self.figure, ax = plt.subplots()
        ax.plot(days, values)

        for xy in zip(days, values):
            ax.annotate('(%s)' % "%.1f" % xy[1], xy=xy)

        ax.set_title(self.title)
        ax.set_xlabel('Day')
        ax.set_ylabel('Average')
        ax.grid(True)

        plt.grid()
        monthsFmt = DateFormatter("%d, %b, '%y")

        ax.xaxis.set_major_formatter(monthsFmt)
        ax.autoscale_view()

        self.figure.autofmt_xdate()
