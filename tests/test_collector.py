# -*- encoding: utf-8 -*-

import unittest.mock

import pytest

from yafl import collector


TEST_RESOURCE="""\
<html>
    <head>
        <title>Test page</title>
    </head>
    <body>
        <h1>Test page</h1>
    </body>
</html>
"""


def mock_resource_string(pkg_name: str, page_path: str) -> str:
    if page_path == '/an/existing/page':
        return TEST_RESOURCE
    raise Exception


@unittest.mock.patch('pkg_resources.resource_string', mock_resource_string)
def test_print_page():
    result = collector.print_page('/an/existing/page')

    assert result == TEST_RESOURCE

    with pytest.raises(IOError):
        collector.print_page('/non/existing/path')


def test_Collector():
    from yafl import conf
    test_app = collector.Collector('test_collector', conf.CONF)

    assert test_app.name == 'test_collector'
    assert test_app.db_path == conf.CONF['db_path']
    assert test_app.db is None
    assert test_app.logger.level == conf.CONF['log_level']
