#!/usr/bin/env python

import gi
import datetime
import logging

from glucose.model import Reading, Category
from glucose.plots.loader import load_plots, close_plot

from glucose import helpers

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject

import os
import signal
import sys


_HERE = os.path.dirname(sys.modules[__name__].__file__)

logger = logging.getLogger(__name__)


class Readings(object):
    COLUMNS = [
        {
            "display_name": "Value", "field": "value", "transform":
            Reading.format_value
        },
        {"display_name": "Category", "field": "category",
         "transform": lambda c: c.name},
        {"display_name": "Date", "field": "created",
         "transform": lambda d: d.strftime("%Y-%m-%d")},
        {"display_name": "Time", "field": "created",
         "transform": lambda t: t.strftime("%H:%M")},
        {"display_name": "Notes", "field": "notes"},
    ]

    def __init__(self, view):
        self.view = view
        self.setup_columns()

    def setup_columns(self):
        for i, col in enumerate(self.COLUMNS):
            if not col.get("visible", True):
                continue

            renderer = col.get("renderer", Gtk.CellRendererText())

            if isinstance(renderer, Gtk.CellRendererPixbuf):
                column = Gtk.TreeViewColumn(markup=0)
                column.set_title(col["display_name"])
                column.pack_start(renderer, expand=False)
                column.add_attribute(renderer, "pixbuf", i)
            else:
                column = Gtk.TreeViewColumn(col["display_name"],
                                            renderer, markup=i)

            col_number = col.get("sort_col", i)
            column.set_sort_column_id(col_number)

            self.view.append_column(column)

    def show(self, readings):
        model = Gtk.ListStore(*([i.get("type", str)
                                 for i in self.COLUMNS] + [object]))
        for reading in readings:
            row = []
            for item in self.COLUMNS:
                if "transform" in item:
                    value = item["transform"](getattr(reading, item['field']))
                else:
                    value = str(getattr(reading, item["field"], "-"))

                row.append(value)

            row.append(reading)
            model.append(row)

        self.view.set_model(model)
        self.view.show_all()


class Plots(object):

    def __init__(self, view):
        self.view = view

    def show(self):
        childs = self.view.get_children()
        page = self.view.get_current_page()

        if len(childs):
            for child in childs:
                viewport = child.get_children()[0]
                for plot in viewport.get_children():
                    if not isinstance(plot, Gtk.Label):
                        close_plot(plot)
                self.view.remove(child)

        for plot in load_plots():
            scrolled = Gtk.ScrolledWindow()
            try:
                canvas = plot.get_canvas()
            except:
                canvas = Gtk.Label("No Data found")
            scrolled.add_with_viewport(canvas)
            self.view.append_page(scrolled, Gtk.Label(plot.title))

        self.view.show_all()
        self.view.set_current_page(page)


class Stats(object):

    def __init__(self, view):
        self.view = view

    def show(self):
        (low, avg, high) = Reading.get_min_avg_max()
        (total, low_c, normal_c, high_c) = Reading.group_by_range()

        try:
            latest = Reading.get().value
        except:
            latest = 0.0

        helpers.set_numeric_label(self.view, "latest_reading",
                                  latest)
        helpers.set_numeric_label(self.view, "lowest_label",
                                  low)
        helpers.set_numeric_label(self.view, "highest_label",
                                  high)
        helpers.set_numeric_label(self.view, "average_label",
                                  avg)

        helpers.set_numeric_label(self.view, "lows_label", low_c, total)
        helpers.set_numeric_label(self.view, "highs_label", high_c, total)
        helpers.set_numeric_label(self.view, "normal_label", normal_c, total)


class QuickAdd(GObject.GObject):

    __gsignals__ = {
        'reading-added': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
                          (GObject.TYPE_PYOBJECT, )),
    }

    def __init__(self, view):
        GObject.GObject.__init__(self)
        self.view = view

        self.add_btn = self.view.get_object("quick_add_btn")
        self.value = self.view.get_object("quick_add_value")

    def show(self):
        category_store = Gtk.ListStore(str, str)
        categories = Category.select().distinct(Category.name)

        for category in categories:
            category_store.append([category.name, category.name])

        self.categories_combo = self.view.get_object("categories")
        model = self.categories_combo.get_model()

        if model is not None:
            model.clear()

        self.categories_combo.set_model(category_store)
        self.categories_combo.set_active(0)

        self.signals()

    def signals(self):
        self.add_handler = self.add_btn.connect("clicked",
                                                self.add_reading)

    def add_reading(self, widget):
        value = self.value.get_value_as_int()
        tree_iter = self.categories_combo.get_active_iter()

        if not tree_iter:
            return

        model = self.categories_combo.get_model()
        row_id, name = model[tree_iter][:2]

        reading = Reading(value=float(value),
                          created=datetime.datetime.now(),
                          category=Category.get(name=name))
        reading.save()
        self.emit('reading-added', Reading.select())


GObject.type_register(QuickAdd)


class GlucoseAppSignals(object):

    def __init__(self, view):
        self.view = view

    def on_delete(self, *a, **k):
        Gtk.main_quit()


class GlucoseApp(object):

    builder_file = os.path.join(_HERE, 'ui', 'ui.glade')


    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.builder_file)
        self.builder.connect_signals(GlucoseAppSignals(self))

        self.readings = Reading.select()

    def show(self):
        self.readings_treeview.show(self.readings)

        self.stats.show()
        self.plots.show()

        self.quick_add.connect('reading-added', self.on_reading_added)
        self.quick_add.show()

        self.main.show_all()
        Gtk.main()

    def on_reading_added(self, widget, readings):
        #self.builder.get_object('new_reading').show()
        self.readings_treeview.show(readings)
        self.stats.show()

        self.plots.show()

    def quit_now(self, signum, frame):
        Gtk.main_quit()

    @property
    def plots(self):
        try:
            getattr(self, '_plots')
        except AttributeError:
            self._plots = Plots(
                self.builder.get_object("plots"))
        return self._plots

    @property
    def stats(self):
        try:
            getattr(self, '_stats')
        except AttributeError:
            self._stats = Stats(
                self.builder)
        return self._stats

    @property
    def quick_add(self):
        try:
            getattr(self, '_quick_add')
        except AttributeError:
            self._quick_add = QuickAdd(
                self.builder)
        return self._quick_add

    @property
    def readings_treeview(self):
        try:
            getattr(self, '_readings')
        except AttributeError:
            self._readings = Readings(
                self.builder.get_object("readings"))
        return self._readings

    @property
    def main(self):
        return self.builder.get_object("glucose")


def main():
    app = GlucoseApp()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app.show()

if __name__ == "__main__":
    main()
