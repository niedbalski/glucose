from peewee import *
from peewee import create_model_tables

import datetime
import os

database = SqliteDatabase(os.path.join(os.path.dirname(
    os.path.basename(__file__)), 'glucose.sqlite'))


class BaseModel(Model):
    class Meta:
        database = database


class Category(BaseModel):

    DEFAULT_CATEGORIES = [
        "Pre Breakfast",
        "Post Breakfastt",
        "Pre Lunch",
        "Post Lunch",
        "Pre Dinner",
        "Post Dinner",
        "Other"
    ]

    created = DateTimeField(default=datetime.datetime.now())
    name = CharField(unique=True)

    @classmethod
    def initialize(cls):
        if cls.select().count() == 0:
            for category in cls.DEFAULT_CATEGORIES:
                Category(name=category).save()


class Setting(BaseModel):
    name = CharField(unique=True)
    value = TextField()


class Reading(BaseModel):
    DEFAULT_NORMAL_VALUE_LOW = 90.0
    DEFAULT_NORMAL_VALUE_HIGH = 150.0

    DEFAULT_NORMAL_VALUE = (DEFAULT_NORMAL_VALUE_LOW,
                            DEFAULT_NORMAL_VALUE_HIGH)

    created = DateTimeField(unique=True, default=datetime.datetime.now())
    value = FloatField(default=0)
    category = ForeignKeyField(Category, related_name='readings')

    class Meta:
        order_by = ('-created',)

    @classmethod
    def get_min_avg_max(cls, format=None):
        return Reading.select(
            fn.Min(Reading.value),
            fn.Avg(Reading.value),
            fn.Max(Reading.value)
        ).scalar(as_tuple=True)

    @classmethod
    def get_normal_range(cls):
        (setting, _) = Setting.get_or_create(
            name='normal_range',
            value=",".join(map(lambda v: str(v),
                               cls.DEFAULT_NORMAL_VALUE)),
        )
        return map(lambda x: float(x), setting.value.split(","))

    @classmethod
    def group_by_day(cls):
        day = fn.DATE_TRUNC('day', Reading.created)
        return Reading.select(day.alias("day"),
                              fn.Avg(Reading.value).alias("avg")).group_by(
                                  day).order_by(day)

    @classmethod
    def group_by_range(cls):
        (range_l, range_h) = cls.get_normal_range()

        low = Reading.select().where(
            Reading.value < range_l).count()

        high = Reading.select().where(
            Reading.value > range_h).count()

        normal = Reading.select().where(
            Reading.value >= range_l, Reading.value <= range_h).count()

        return Reading.select().count(), low, normal, high

    @classmethod
    def format_value(cls, value):
        (range_l, range_h) = cls.get_normal_range()
        formatted = "<span foreground='{0}'><b>{1}</b></span>"

        if value >= range_l and value <= range_h:
            return formatted.format("green", value)
        elif value <= range_l:
            return formatted.format("orange", value)
        else:
            return formatted.format("red", value)

models = [Category, Reading, Setting]

try:
    create_model_tables(models, fail_silently=True)
    for model in models:
        try:
            getattr(model, 'initialize')()
        except:
            pass
except Exception as ex:
    raise