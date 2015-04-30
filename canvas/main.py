import click
from .gui import GUI
from .transport import Transport

CLIPS = [
    # Clip('testclips/a.wav', start=0, y=0.5),
    # Clip('', start=1.2, length=22, y=0.53, load=False),
    # Clip('', start=0.5, length=0, y=0.55, load=False),
]

@click.command()
@click.option('--mix', default=None, help='Mix down recording to wav file.',
              type=click.Path())
@click.argument('dirname', type=click.Path())
def main(mix, dirname):
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
