# -*- coding: utf-8 -*-

from importlib import import_module
import json
import os
import os.path
import random

from .exceptions import ConfigError, SourceError

SEP = ':'


def get_rnd_item(fpath):
    """Get random item from list read from JSON data.

    :param fpath: the filepath of the JSON containing a list
    :type fpath: str
    :returns: str - a user agent string chosen randomly from list
    """
    try:
        with open(fpath, 'r') as json_file:
            items = json.load(json_file)
    except ValueError as e:
        raise ConfigError(e)
    return random.choice(items)


def get_uuid(*args):
    """Return a UUID built from fragments

    :param \*args: UUID fragments
    :type \*args: str
    :returns: str - a UUID resulting from string concatenation
    """
    return SEP.join(args)


def passthrough_loader(base_uuid, data):
    return {base_uuid: data}


def dig_loader(base_uuid, data):
    _data = {}
    for key, info in data.items():
        name = get_uuid(base_uuid, key)
        _data[name] = info
    return _data


def get_source(name):
    """Get the source object based on a name."""
    # import only occurs when function is called
    from .conf import settings
    if name not in settings['SOURCES']:
        raise SourceError("Unknown source ({})".format(name))
    modname = settings['SOURCES'][name]['modname']
    mod = import_module(modname)
    src = mod.Source(name)
    return src


def load_backend(backend_name):
    """Load a backend based on a module name

    :param backend_name: database backend to use
    :type backend_name: str
    :returns: module
    """
    try:
        return import_module(backend_name)
    except ImportError as e:
        # FIXME add error treatment
        raise


def load_tree(base_dir, data_loader):
    """Create a one-dimensional dictionary given a tree directory structure.

    The keys are generated with a separator per folder depth.

    :param base_dir: a valid directory or path
    :type base_dir: str
    :param data_loader: a function specificying how to name the keys
    :type data_loader: func
    :returns: dict
    """
    tree = {}
    for root, dirs, files in os.walk(base_dir):
        relpath = os.path.relpath(root, base_dir)
        if relpath != os.curdir:
            reluuid = relpath.replace(os.sep, SEP)
        else:
            reluuid = ''

        for file in files:
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r') as jsonfd:
                    data_chunk = json.load(jsonfd)
            except ValueError as e:
                # "No JSON object could be decoded"
                raise ConfigError(e)
            except IOError as e:
                raise ConfigError("{} ({})"
                                  .format(e.strerror, filepath))
            src_name = os.path.splitext(file)[0]
            if reluuid == '':
                uuid_key = src_name
            else:
                uuid_key = SEP.join((reluuid, src_name))
            tree.update(data_loader(uuid_key, data_chunk))

    return tree
