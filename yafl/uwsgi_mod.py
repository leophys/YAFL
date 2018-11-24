# -*- encoding: utf-8 -*-
"""
This module is an adaptor to allow uWSGI to serve the app.
It defines a `yafl` callable that should be invoked by
uWSGI.
"""
from yafl import collector
from yafl import conf

yafl = collector.create_app("wsgi_collector", conf=conf.CONF)
