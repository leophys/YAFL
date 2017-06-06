from collector import create_app

if __name__ == "__main__":
    conf = {
        "addresses": "127.0.0.1",
        "port": 8081,
        "db_path": "default_db.json"
    }
    app = create_app("wsgi_collector", conf)
    app.run(
        host = conf['addresses'],
        port = int(conf['port'])
    )
