# -*- coding: utf-8 -*-

from .utils import get_source

from celery import Celery
from celery.utils.log import get_task_logger


app = Celery('okq')
app.config_from_object('celeryconfig')
logger = get_task_logger(__name__)


@app.task
def scrape(name):
    src = get_source(name)
    src.scrape()
