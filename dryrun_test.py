from collector import create_app

conf = {
    "db_path": "dryrun_db.json"
}
app = create_app("wsgi_collector", config=conf)

if __name__ == "__main__":
    app.run(host='127.0.0.1',port=8081)
