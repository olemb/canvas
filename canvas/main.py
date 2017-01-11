import os
import time
import click
from .gui import GUI
from .transport import Transport

CLIPS = [
    # Clip('testclips/a.wav', start=0, y=0.5),
    # Clip('', start=1.2, length=22, y=0.53, load=False),
    # Clip('', start=0.5, length=0, y=0.55, load=False),
]

def get_dirname():
    return os.path.expanduser('~/Desktop/canvas-{:d}'.format(int(time.time())))


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
        gui = GUI(dirname)
        gui.transport.load()
        try:

            try:
                gui.run()
            except KeyboardInterrupt:
                pass
        finally:
            gui.quit()
