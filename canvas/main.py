import os
import time
import click
from contextlib import closing
from .gui import GUI
from .transport import Transport


def get_dirname():
    now = int(time.time())
    return os.path.expanduser(f'~/Desktop/canvas-{now}')


@click.command()
@click.option('--mix', default=None, help='Mix down recording to wav file.',
              type=click.Path())
@click.argument('dirname', type=click.Path(), nargs=-1)
def main(mix, dirname):
    if len(dirname) == 0:
        dirname = get_dirname()
    elif len(dirname) == 1:
        dirname = dirname[0]
    else:
        raise click.ArguementError('too many arguments')

    if mix:
        transport = Transport(dirname)
        transport.load()
        transport.save_mix(mix)
    else:
        with closing(GUI(dirname)) as gui:
            gui.transport.load()
            gui.run()
