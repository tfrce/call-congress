# Misc utilities that are useful between models

import itertools
import json
from flask import Markup


def choice_keys(choices):
    return [str(key) for key in choices.keys()]


def choice_values(choices):
    return [str(val) for val in choices.values()]


def choice_values_flat(choices):
    # flatten nested lists
    return list(itertools.chain(*choices.values()))


def choice_items(choices):
    return [(str(val), key) for val, key in choices.items()]


def json_markup(obj):
    return Markup(json.dumps(obj))
