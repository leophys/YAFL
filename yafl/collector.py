# -*- encoding: utf-8 -*-
"""
This is the module that contains the main logic.
It defines a class called `Collector` that customizes some
bits of a Flask app (initializing the database, for example),
and a `create_app` function that adds the routes to the app,
managing them with the appropriate behaviour.
Here is also defined a `print_page` function
"""
import collections
import datetime
import logging
import pkg_resources
import queue
import sys

from flask import Flask, request
from tinydb import TinyDB

from yafl.FLexceptions import (
    PostError, UnknownError, ConfigError, DBInsertError
)
from yafl import mailer


def print_page(page_path):
    try:
        page = pkg_resources.resource_string(__name__, page_path)
        return page
    except:
        raise IOError


class Collector(Flask):
    client_timemap = {}

    def __init__(self, import_name, conf):
        super(Collector, self).__init__(import_name)
        self.db_path = conf['app']['db_path']
        self.address = conf['app']['address']
        self.port = conf['app']['port']
        self.db = None
        self.logger.setLevel(conf['app']['log_level'])
        if conf['app']['log_level'] <= logging.DEBUG:
            self.debug = True
        self.mailer = None
        if conf['mail'].get('address') is not None:
            mailconf = conf['mail']
            if 'event_timeout' in mailconf.keys():
                self.timeout = mailconf['event_timeout']
                mailconf.pop('event_timeout')
            else:
                self.timeout = datetime.timedelta(minutes=5)
            # Infinite length queue! To store infinite events.
            self.queue = queue.Queue(-1)
            self.mailer = mailer.Mailer(
                queue=self.queue, daemon=True, **mailconf, logger=self.logger
            )
        if self.mailer:
            self.logger.debug("Starting the mailer in a separate thread...")
            self.mailer.start()
            self.logger.debug("Mailer thread started.")

    def init_db(self):
        try:
            self.db = TinyDB(self.db_path)
            self.logger.info("db init'd (%s)", self.db_path)
        except IOError:
            self.logger.error("db init failed")
            raise ConfigError
        except Exception as e:
            raise UnknownError(e)

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
        except Exception as e:
            raise DBInsertError(e)

    def contact_from_client(self, client_ip):
        if client_ip not in self.client_timemap.keys():
            self.client_timemap[client_ip] = collections.namedtuple(
                'client',
                ['first_contact', 'last_contact']
            )
            self.client_timemap[client_ip].first_contact = datetime.datetime.now()
        self.client_timemap[client_ip].last_contact = datetime.datetime.now()

    def run(self, *args, **kwargs):
        super().run(
            host=self.address,
            port=self.port,
            *args, **kwargs
        )

    def maybe_send_mail(self, ip):
        if hasattr(self, 'queue'):
            if ip not in self.client_timemap.keys():
                self.logger.debug("Sending first contact mail.")
                self.queue.put(
                    ("First contact from {}".format(ip),
                     ip)
                )
                return
            if self.client_timemap[ip].last_contact - datetime.datetime.now() > self.timeout:
                self.logger.debug("Revamped interest mail.")
                self.queue.put(
                    ("Credentials from {}".format(ip),
                     ip)
                )
            self.logger.debug(
                "%s - first: %s  last: %s",
                ip,
                self.client_timemap[ip].first_contact,
                self.client_timemap[ip].last_contact
            )
        return


def get_client_ip(request):
    """
    Returns the proper client ip, looking for
    "X-Forwarded-For"
    "X-Forwarded-Host"
    "X-Client-IP"
    "X-Real-IP"
    headers first.
    """
    headers = dict(
        (h.lower(), h_value) for h, h_value in request.headers.items()
    )
    if 'x-forwarded-for' in headers:
        return headers['x-forwarded-for']
    if 'x-forwarded-host' in headers:
        return headers['x-forwarded-host']
    if 'x-client-ip' in headers:
        return headers['x-client-ip']
    if 'x-real-ip' in headers:
        return headers['x-real-ip']
    return request.remote_addr


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
        except Exception as e:
            app.logger.error("UnknownError: %s", e)
            raise UnknownError(e)

    @app.route("/js/<jspath>")
    def js_serve(jspath):
        try:
            return print_page("webassets/js/{}".format(jspath))
        except IOError:
            app.logger.error(" js/{} not readable".format(jspath))
            raise ConfigError
        except Exception as e:
            app.logger.error("UnknownError: %s", e)
            raise UnknownError(e)

    @app.route("/login", methods=['POST'])
    def collect():
        try:
            user = request.form.getlist('u')
            password = request.form.getlist('p')
            now = format(datetime.datetime.now())
            ip = get_client_ip(request)
            data = {
                "user": user,
                "password": password,
                "time": now,
                "ip": ip
            }
            app.add_to_db(data)
            app.maybe_send_mail(ip)
            app.contact_from_client(ip)
            return print_page("webassets/wrong_login.html")
        except IOError:
            app.logger.error("webassets/wrong_login.html not readable")
            raise ConfigError
        except Exception as e:
            app.logger.error("PostError: %s", e)
            raise PostError(e)

    return app
