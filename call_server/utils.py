# Misc utilities that are useful between models

import itertools
import json
from collections import OrderedDict

from flask import Markup


def convert_to_dict(obj):
    """converts tuples of tuples to OrderedDict for easy lookup that maintains order"""
    if type(obj) is not dict():
        try:
            dictlike = OrderedDict(obj)
            return dictlike
        except ValueError:
            pass
    return obj


def choice_keys(choices):
    choices = convert_to_dict(choices)
    return [str(key) for key in choices.keys()]


def choice_values(choices):
    choices = convert_to_dict(choices)
    return [str(val) for val in choices.values()]


def choice_values_flat(choices):
    choices = convert_to_dict(choices)
    # flatten nested lists
    return list(itertools.chain(*choices.values()))


def choice_items(choices):
    choices = convert_to_dict(choices)
    return [(str(val), key) for val, key in choices.items()]


def json_markup(obj):
    return Markup(json.dumps(obj))
