from collector import create_app

conf = { "db_path": "/tmp/test_run_db.json" }
yafl = create_app("wsgi_collector", config=conf)
