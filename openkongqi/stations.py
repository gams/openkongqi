# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from .conf import settings
from .utils import get_uuid, load_tree, passthrough_loader


_STATIONS_MAP = load_tree(settings['STATIONS_MAP_DIR'],
                          data_loader=passthrough_loader)


def get_station_map(uuid=None):
    """Get the entire station map given a UUID,
    or get the concatenated station map from multiple cities/regions given a UIID with a wildcard "*"

    Usage::
        >>> from openkongqi.stations import get_station_map
        >>> get_station_map('cn:guangdong:guangzhou') # get the station map from Guangzhou, Guangdong
        >>> get_station_map('cn:guangdong:*') # get the concatenated station map from all cities in Guangdong province
        >>> get_station_map('cn:*') # get the concatenated station map from all cities and provinces in China
        ...

    :param uuid: a UUID key
    :type uuid: str
    """
    if uuid.endswith("*") is True:
        id_map = {}
        for k in _STATIONS_MAP.keys():
            if k.startswith(uuid[:-1]):
                id_map.update(_STATIONS_MAP[k])
    else:
        id_map = _STATIONS_MAP.get(uuid, {})
    return id_map


def get_all_uuids():
    """Return a sorted list of complete station UUIDs."""
    res = []
    for country, station_map in _STATIONS_MAP.items():
        res.extend([get_uuid(country, s) for s in station_map.values()])
    return sorted(res)
