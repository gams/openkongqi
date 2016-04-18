# -*- coding: utf-8 -*-

from importlib import import_module

from .conf import settings
from .exceptions import SourceError

from celery import Celery
from celery.utils.log import get_task_logger


app = Celery('okq')
app.config_from_object('celeryconfig')
logger = get_task_logger(__name__)


@app.task
def fetch(name):
    if name not in settings['SOURCES']:
        raise SourceError("Unknown source ({})".format(name))
    modname = settings['SOURCES'][name]['modname']
    mod = import_module(modname)
    src = mod.Source(name)
    src.scrape()
