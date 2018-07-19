# -*- encoding: utf-8 -*-
"""
This module contains the Exceptions. Right now, are all dummy,
meaning that they all `pass`.
"""

class PostError(Exception):
    pass

class ConfigError(Exception):
    pass

class UnknownError(Exception):
    pass

class DBInsertError(Exception):
    pass
