# -*- encoding: utf-8 -*-
"""
This module provides the configuration facility for YAFL.

Given a configuration parameter, the order in which it is
processed is the following:
    - An environment variable (prefixed by 'YAFL_') al caps
    - The value of the parameter in a configuration file
    - A default value, included in this file
The order in which the configuration files are searched is:
    - $PWD/.yafl.{yaml,yml}
    - ~/.yafl.{yaml,yml}
    - /etc/yafl.{yaml,yml}
    - The path to a file in the environment variable YAFL_CONF_PATH
"""

from datetime import datetime
import logging
import os

import yaml


_NOW = datetime.now().strftime("%y-%m-%d_%H:%M:%S")


_CONFIG_PATHS = (
    os.path.join(os.curdir, '.yafl.yaml'),
    os.path.join(os.curdir, '.yafl.yml'),
    os.path.join(os.path.expanduser('~'), '.yafl.yaml'),
    os.path.join(os.path.expanduser('~'), '.yafl.yml'),
    '/etc/yafl.yaml',
    '/etc/yafl.yml',
    os.environ.get('YAFL_CONF_PATH'),
)


_CONF = {}


for config_path in _CONFIG_PATHS:
    try:
        if config_path is not None:
            with open(config_path) as cf:
                _CONF = yaml.safe_load(cf)
    except IOError:
        pass


_CONF_KEYS = [
    ('db_path', '/tmp/yafl_%r.json' % _NOW),
    ('log_level', logging.INFO),
    ('address', '127.0.0.1'),
    ('port', 8081),
]


CONF = {}


for k in _CONF_KEYS:
    CONF_ENV_VAR = 'YAFL_' + k[0].upper()
    if CONF_ENV_VAR in os.environ.keys():
        CONF[k[0]] = os.environ.get(CONF_ENV_VAR)
    else:
        try:
            CONF[k[0]] = _CONF[k[0]]
        except KeyError:
            CONF[k[0]] = k[1]
