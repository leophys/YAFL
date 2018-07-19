# -*- encoding: utf-8 -*-
"""
This module defines the command line entry point.
"""

import click

from . import collector
from . import conf


@click.command()
@click.option('-a', '--address', type=str,
              default=conf.CONF['address'],
              help="Address to bind. If no configuration given, defaults to 127.0.0.1")
@click.option('-p', '--port', type=int,
              default=conf.CONF['port'],
              help="Port to bind to. If no configuration given, defaults to 8081")
@click.option('-o', '--output', type=str,
              default=conf.CONF['db_path'],
              help="Path to log file. If no configuration given, " +\
              "defaults to /tmp/yafl_<current_time>.json")
@click.option('--debug/--no-debug', default=False,
              help="Toggles debug (verbose output)")
def cli_run(address: str, port: int, output: str, debug: bool):
    """
    Command line entry point.

    :param address: the address to bind YAFL to.
    :param port: the port to bind YAFL to.
    :param output: the db json file where to output the results.
    :param debug/nodebug: whether to toggle the log level to debug or not.
    """
    print(format(output))
    log_level = 'DEBUG' if debug else conf.CONF['log_level']
    yafl = collector.create_app("cli_run", conf={'db_path': output, 'log_level': log_level})
    yafl.run(host=address, port=port)

if __name__ == '__main__':
    cli_run()
