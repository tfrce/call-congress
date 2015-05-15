# Misc utilities that are useful between models
from flask import current_app, flash

import itertools
import json
from collections import OrderedDict

from flask import Markup
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError


# near copy of django's get_or_create, modified from http://stackoverflow.com/a/21146492/264790
def get_one_or_create(session,
                      model,
                      create_method='',
                      create_method_kwargs=None,
                      **kwargs):
    """ get one model object from keyword parameters, or create one and save it
    returns the object and boolean true if created"""
    try:
        return session.query(model).filter_by(**kwargs).one(), False
    except NoResultFound:
        kwargs.update(create_method_kwargs or {})
        created = getattr(model, create_method, model)(**kwargs)
        try:
            session.add(created)
            session.commit()
            session.flush()
            return created, True
        except IntegrityError, e:
            current_app.logger.error('get_one_or_create failed for '+model+' '+kwargs+e)
            flash("Unable to create "+model, 'error')
            session.rollback()
            return session.query(model).filter_by(**kwargs).one(), False


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
