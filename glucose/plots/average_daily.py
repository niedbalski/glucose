#!/usr/bin/env python

from glucose.plots.base import Plot
from glucose.model import Reading

from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt

import datetime


class AverageReadingsDaily(Plot):

    title = "Average Glucose Readings Daily"

    def __init__(self, from_date=None):
        Plot.__init__(self)

        values, days = self.get_data(from_date=from_date)

        self.figure, ax = plt.subplots()
        self.lines, = ax.plot(days, values)

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
        self.ax = ax

    def refresh(self, from_date=None):
        values, days = self.get_data(from_date=from_date)

        self.ax.clear()
        self.ax.plot(days, values)

        for xy in zip(days, values):
            self.ax.annotate('(%s)' % "%.1f" % xy[1], xy=xy)

        self.ax.set_title(self.title)
        self.ax.set_xlabel('Day')
        self.ax.set_ylabel('Average')

        self.figure.canvas.draw_idle()

    def get_data(self, from_date=None):
        grouped_readings = Reading.group_by_day(from_date=from_date)

        x = [x.avg for x in grouped_readings]
        y = [datetime.datetime.strptime(
            y.day, '%Y-%m-%d') for y in grouped_readings]

        return x, y
