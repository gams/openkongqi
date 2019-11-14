# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from datetime import datetime
import os
import shutil

from .exceptions import CacheError

FILENAME = "{key}-{ts}.txt"


class FileCache(object):
    """Simple file caching based on a key name and content.
    """
    def __init__(self, folder_name):
        if os.path.isabs(folder_name):
            self.cachepath = folder_name
        else:
            self.cachepath = os.path.join(
                os.getcwd(),
                folder_name)
        if not os.path.exists(self.cachepath):
            try:
                os.makedirs(self.cachepath)
            except OSError as e:
                raise CacheError(
                    'cache creation problem ({})'.format(e.strerror))

    def get_fp(self, key, ts=None):
        # TODO doc
        if ts is None:
            ts = datetime.now()

        return os.path.join(self.cachepath,
                            FILENAME.format(key=key,
                                            ts=ts.strftime('%Y%m%d%H%M%S')))

    def get_latest_fp(self, key):
        # TODO doc
        return os.path.join(self.cachepath,
                            FILENAME.format(key=key, ts='latest'))

    def set(self, key, fsrc, ts=None):
        # TODO doc
        filename = self.get_fp(key, ts)
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as e:
                raise CacheError(
                    'cache creation problem ({})'.format(e.strerror))
        fdst = open(filename, 'wb')
        shutil.copyfileobj(fsrc, fdst)
        filelink = self.get_latest_fp(key)
        if os.path.lexists(filelink):
            os.remove(filelink)
        os.symlink(os.path.basename(filename), filelink)

    def get(self, key, ts=None):
        # TODO doc
        try:
            fd = open(self.get_fp(key, ts), 'r')
        except IOError:
            return
        return fd

    def get_latest(self, key):
        try:
            fd = open(self.get_latest_fp(key), 'r')
        except IOError:
            return
        return fd
