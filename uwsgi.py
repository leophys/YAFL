from collector import create_app

conf = {
    "addresses": "127.0.0.1",
    "port": 8081,
    "db_path": "default_db.json"
}
yafl = create_app("wsgi_collector", conf)

if __name__ == "__main__":
    yafl.run(
        host = conf['addresses'],
        port = int(conf['port'])
    )
