#!/usr/bin/env python


def format_as_percent(value, total, tpl, *a, **k):
    try:
        percent = (1.0 * value/total) * 100

        a = map(lambda x: str(x), a)
        a.append(str("%.2f" % percent))
        tpl = tpl + " ({}%)"
        return tpl.format(*tuple(a))
    except ZeroDivisionError:
        return "0 (0%)"


def set_numeric_label(view, label, value, *a, **k):
    label = view.get_object(label)
    total = k.get('total', None)
    if total:
        return label.set_text(format_as_percent(
            value, total, "{} ", *a))
    if value in (None, ):
            value = str(0.0) + ' (0%)'
    elif not isinstance(value, str):
        if isinstance(value, float):
            value = "%.1f" % value
        value = str(value)
    return label.set_text(value)
