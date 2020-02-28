# -*- coding: utf-8 -*-
from openkongqi.source import get_source


def source_router(name, args, kwargs, options, task=None):
    """
    A dynamic router used to set a specific queue to scrape a source if the
    source definition has a key named 'queue'.

    .. code:: json

        {
          "taiwan": {
            "target": "https://taqm.epa.gov.tw/pm25/en/PM25A.aspx?area=10",
            "uuid": "tw",
            "modname": "okq_gams.source.taqm",
            "tz": "Asia/Taipei",
            "queue": "taiwan"
          }
        }
        
    """
    if name == 'openkongqi.tasks.scrape':
        info = get_source(args[0])
        if 'queue' in info:
            return {
                'queue': info['queue'],
                'routing_key': info['queue'],
            }
        else:
            return None
