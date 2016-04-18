# -*- coding: utf-8 -*-


class OpenKongqiError(Exception):
    pass


class ConfigError(OpenKongqiError):
    pass


class CacheError(OpenKongqiError):
    pass


class SourceError(OpenKongqiError):
    pass


class FeedError(OpenKongqiError):
    pass


class UUIDNotFoundError(OpenKongqiError):
    pass
