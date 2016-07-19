# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from datetime import datetime
from inspect import getmodulename
import logging
import re

from .base import HTTPSource
from ..conf import logger

import bs4

logger = logging.getLogger("openkongqi.source.{}"
                           .format(getmodulename(__file__)))


class Source(HTTPSource):
    """Source class for pm25.in providing China environment data

    Extract data from http://pm25.in/, data table rows are as follow:

    * 0 - Monitoring name
    * 1 - AQI
    * 2 - AQI category in Chinese
    * 3 - primary pollutant
    * 4 - PM2.5
    * 5 - PM10
    * 6 - CO
    * 7 - NO2
    * 8 - O3 (1h average)
    * 9 - O3 (8h average)
    * 10 - SO2
    """

    key_context = {
        u'moduuid': 'pm25in',
    }
    #: regexp matching null characters
    null_re = re.compile(r'_')

    def extract(self, content):
        # Avoid warnings of bs4>=4.4 by explicitly stating parser
        soup = bs4.BeautifulSoup(content, "html5lib")
        time = soup.find(class_="live_data_time").p.text
        ts = datetime.strptime(time.split(u'\uff1a')[1],
                               '%Y-%m-%d %H:%M:%S').replace(tzinfo=self._tz)
        data = {}
        for row in soup.find(id='detail-data').find_all('tr')[1:]:
            cells = row.find_all('td')
            try:
                station = self.get_station_uuid(cells[0].string)
                data[station] = []
            except KeyError as e:
                logger.warning("Station not found ({}); skipping ..."
                               .format(e.message))
            else:
                data[station].append(
                    {
                        'ts': ts,
                        'fields': {
                            'pm25': self.pythonify(cells[4].string, is_num=True),
                            'pm10': self.pythonify(cells[5].string, is_num=True),
                            'co': self.pythonify(cells[6].string, is_num=True),
                            'no2': self.pythonify(cells[7].string, is_num=True),
                            'o3_1h': self.pythonify(cells[8].string, is_num=True),
                            'o3_8h': self.pythonify(cells[9].string, is_num=True),
                            'so2': self.pythonify(cells[10].string, is_num=True),
                        },
                    }
                )
        return data
