from collector import create_app
import click
#import os

@click.command()
@click.option('-a', '--address', type=str,
              default='127.0.0.1',
              help="Address to bind. Defaults to 127.0.0.1")
@click.option('-p', '--port', type=int,
              default=8081,
              help="Port to bind to. Defaults to 8081")
@click.option('-l', '--log', type=str,
              default='/tmp/cli_db.json',
              help="Path to log file. Defaults to ./default_db.json")
def cli_run(address='127.0.0.1', port=8081, log='/tmp/cli_db.json'):
    print(format(log))
    yafl = create_app("cli_run", config={'db_path': log})
    yafl.run(host=address, port=port)

if __name__ == '__main__':
    cli_run()
