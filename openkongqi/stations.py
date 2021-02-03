# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals
from copy import deepcopy

from .conf import settings
from .utils import get_uuid, load_tree, passthrough_loader, SEP, WILDCARD


_STATIONS_MAP = load_tree(settings['STATIONS_MAP_DIR'],
                          data_loader=passthrough_loader)


def get_station_map(uuid=None):
    """Get the entire station map given a UUID, or get the concatenated station
    map from multiple cities/regions given a UIID with a wildcard "*"

    Usage::

        >>> from openkongqi.stations import get_station_map
        >>> get_station_map('th') # get the station map of Thailand
        >>> get_station_map('th:*') # get the station map of Thailand
        >>> get_station_map('cn:guangdong') # get the station map of Guangdong province
        >>> get_station_map('cn:*') # get the concatenated station map of all provinces in China

    :param uuid: a UUID key
    :type uuid: str
    """
    if uuid.endswith(SEP + WILDCARD) is True:
        id_map = {}
        uuid_without_wildcard = uuid[:-2]
        for k in _STATIONS_MAP:
            if k.startswith(uuid_without_wildcard):
                if uuid_without_wildcard == k:
                    id_map.update(_STATIONS_MAP.get(k, {}))
                else:
                    prefix = k.replace(uuid_without_wildcard + SEP, "", 1)
                    new_map = _inject_uuid_prefix(prefix, _STATIONS_MAP[k])
                    id_map.update(new_map)

    else:
        id_map = _STATIONS_MAP.get(uuid, {})
    return id_map


def get_all_uuids():
    """Return a sorted list of complete station UUIDs."""
    res = []
    for country, station_map in _STATIONS_MAP.items():
        res.extend([get_uuid(country, s) for s in station_map.values()])
    return sorted(res)


def _inject_uuid_prefix(prefix, station_map):
    map_copy = deepcopy(station_map)
    for station in map_copy:
        map_copy[station]["uuid"] = get_uuid(prefix, map_copy[station]["uuid"])
    return map_copy
