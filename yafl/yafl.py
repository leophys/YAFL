# -*- encoding: utf-8 -*-

import click

from yafl.collector import create_app


@click.command()
@click.option('-a', '--address', type=str,
              default='127.0.0.1',
              help="Address to bind. Defaults to 127.0.0.1")
@click.option('-p', '--port', type=int,
              default=8081,
              help="Port to bind to. Defaults to 8081")
@click.option('-o', '--output', type=str,
              default='/tmp/cli_db.json',
              help="Path to log file. Defaults to /tmp/cli_db.json")
@click.option('--debug/--no-debug', default=False,
              help="Toggles debug (verbose output)")
def cli_run(address: str, port: int, output: str, debug: bool):
    print(format(output))
    log_level = 'DEBUG' if debug else 'INFO'
    yafl = create_app("cli_run", config={'db_path': output, 'log_level': log_level})
    yafl.run(host=address, port=port)

if __name__ == '__main__':
    cli_run()
