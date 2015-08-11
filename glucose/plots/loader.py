#!/usr/bin/env python

from glucose import plots

import inspect

import matplotlib.pyplot as plt


def close_plot(fig):
    plt.close(fig.figure)


def load_plots(from_date=None):
    for attribute in dir(plots):
        attribute = getattr(plots, attribute)
        if inspect.isclass(attribute) and issubclass(
                attribute, plots.base.Plot) and attribute.__name__ != 'Plot':
            yield attribute(from_date=from_date)
