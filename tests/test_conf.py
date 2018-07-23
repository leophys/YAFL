# -*- encoding: utf-8 -*-

import importlib
import io
import os
import unittest.mock

# This is appropriate *BEFORE* the import of the conf module
os.environ['YAFL_CONF_PATH'] = '/a/random/path'

from yafl import conf


CONF_PATHS = conf._CONFIG_PATHS
TEST_CONFIG =\
"""---
db_path: %s
log_level: 'DEBUG'
address: '127.0.0.11'
port: 8090
"""
EXISTING_CONF = []


def create_conf_file(conf_path: str):
    with open(conf_path, "w") as cf:
        cf.write(TEST_CONFIG % conf_path)


def mock_open(conf_path: str, mode: str="r") -> io.BytesIO:
    if conf_path in EXISTING_CONF:
        return io.BytesIO((TEST_CONFIG % conf_path).encode())
    raise IOError


@unittest.mock.patch('builtins.open', mock_open)
def test_CONF_no_file():
    importlib.reload(conf)

    result = conf.CONF['db_path']

    assert '/tmp/yafl_' in result
    assert 'json' in result


@unittest.mock.patch('builtins.open', mock_open)
def test_CONF_order():
    for conf_path in CONF_PATHS:
        EXISTING_CONF.append(conf_path)
        importlib.reload(conf)

        result = conf.CONF['db_path']

        assert result == conf_path
