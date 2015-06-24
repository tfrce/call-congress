# Misc utilities that are useful between models
from flask import current_app, flash

import itertools
import json
import yaml
import yaml.constructor

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


class OrderedDictYAMLLoader(yaml.Loader):
    """
    A YAML loader that loads mappings into ordered dictionaries.
    From https://gist.github.com/enaeseth/844388
    Probably won't work with deeply nested dicts. YMMV
    """

    def __init__(self, *args, **kwargs):
        yaml.Loader.__init__(self, *args, **kwargs)

        self.add_constructor(u'tag:yaml.org,2002:map', type(self).construct_yaml_map)
        self.add_constructor(u'tag:yaml.org,2002:omap', type(self).construct_yaml_map)

    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructorError(None, None,
                'expected a mapping node, but found %s' % node.id, node.start_mark)

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError, exc:
                raise yaml.constructor.ConstructorError('while constructing a mapping',
                    node.start_mark, 'found unacceptable key (%s)' % exc, key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping
