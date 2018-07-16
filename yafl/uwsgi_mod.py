# -*- encoding: utf-8 -*-

from yafl.collector import create_app

conf = {
    "db_path": "/tmp/test_run_db.json",
    "log_level": "DEBUG",
}
yafl = create_app("wsgi_collector", config=conf)
