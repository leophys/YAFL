# -*- encoding: utf-8 -*-
"""
This module defines the command line entry point.
"""

import logging
import queue
import sys
import threading

import click

from yafl import collector
from yafl import conf
from yafl import mailer



@click.command()
@click.option('-a', '--address', type=click.STRING,
              default=conf.CONF['app']['address'],
              help="Address to bind. If no configuration given, "
              "defaults to 127.0.0.1")
@click.option('-p', '--port', type=click.INT,
              default=conf.CONF['app']['port'],
              help="Port to bind to. If no configuration given, "
              "defaults to 8081")
@click.option('-o', '--output', type=click.Path(),
              default=conf.CONF['app']['db_path'],
              help="Path to log file. If no configuration given, " +
              "defaults to /tmp/yafl_<current_time>.json")
@click.option('-m', '--mailserver', type=click.STRING,
              default=conf.CONF['mail']['address'],
              help="The url to of the mailserver (should be the MX record "
              "of your mail domain). If missing, the mailer is disabled.")
@click.option('-r', '--mailport', type=click.INT,
              default=conf.CONF['mail']['port'],
              help="The port to use to connect to the mailserver. "
              "Errors if -m/--mailserver is missing.")
@click.option('-u', '--username', type=click.STRING,
              default=conf.CONF['mail']['username'],
              help="The username to use to log onto your SMTP relay. "
              "Errors if -m/--mailserver is missing.")
@click.option('-w', '--password', type=click.STRING,
              default=conf.CONF['mail']['password'],
              help="The password to use to log onto your SMTP relay. "
              "Errors if -m/--mailserver is missing.\n"
              "DANGEROUS! May persist in the shell history! "
              "Use the configuration file instead!")
@click.option('-f', '--fromfield', type=click.STRING,
              default=conf.CONF['mail']['from_field'],
              help="Sets the From: in the mail sent. "
              "Errors if -m/--mailserver is missing.")
@click.option('-t', '--tofield', type=click.STRING,
              default=conf.CONF['mail']['to_field'],
              help="Sets the To: in the mail sent. MANDATORY. "
              "Errors if -m/--mailserver is missing.")
@click.option('-s', '--starttls', type=click.BOOL,
              default=conf.CONF['mail']['starttls'],
              help="Use STARTTLS connecting to the mailserver. "
              "Errors if -m/--mailserver is missing.")
@click.option('-c', '--config', type=click.File('r'),
              help="Path to a configuration file. If given, "
              "bypasses all the YAFL configuration hierarchy. "
              "Wants to be alone. Fails if other options are given.")
@click.option('--debug/--no-debug', default=False,
              help="Toggles debug (verbose output)")
def cli_run(address: str,
            port: int,
            output: str,
            mailserver: str,
            mailport: int,
            username: str,
            password: str,
            fromfield: str,
            tofield: str,
            starttls: bool,
            config: str,
            debug: bool):
    """
    Command line entry point.
    """
    excluded_keys = [
        mailport,
        username,
        password,
        fromfield,
        tofield,
        starttls
    ]
    if mailserver is None and any(el is not None for el in excluded_keys):
        print("Error: missing 'mailserver' configuration but "
              "dependent flag.", file=sys.stderr)
        sys.exit(-1)
    excluded_keys.extend([address, port, output])
    if config is not None and any(el is not None for el in excluded_keys):
        print("Error: --config must be used alone.", file=sys.stderr)
        sys.exit(-2)
    configuration = {'app': {}, 'mail': {}}
    configuration['app']['db_path'] = output
    configuration['app']['address'] = address
    configuration['app']['port'] = port
    configuration['app']['log_level'] = logging.DEBUG if debug \
        else conf.CONF['app']['log_level']

    if mailserver is not None:
        configuration['mail']['address'] = mailserver
        configuration['mail']['port'] = mailport
        configuration['mail']['username'] = username
        configuration['mail']['password'] = password
        configuration['mail']['from_field'] = fromfield
        configuration['mail']['to_field'] = tofield
        configuration['mail']['starttls'] = starttls

    if config is not None:
        # Bypass all the conf logic
        configuration = conf.load_from_file(config)
        address = configuration['app']['address']
        port = configuration['app']['port']

    configuration = conf.validate_conf(configuration)

    if debug:
        print(format(output))

    yafl = collector.create_app(
        "cli_run",
        conf=configuration
    )
    yafl.run()


if __name__ == '__main__':
    cli_run()
