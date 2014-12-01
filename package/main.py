import click
from .gui import GUI

CLIPS = [
    # Clip('testclips/a.wav', start=0, y=0.5),
    # Clip('', start=1.2, length=22, y=0.53, load=False),
    # Clip('', start=0.5, length=0, y=0.55, load=False),
]

@click.command()
@click.argument('dirname')
def main(dirname):
    gui = GUI(dirname)
    gui.transport.load()
    try:
        
        try:
            gui.run()
        except KeyboardInterrupt:
            pass
    finally:
        gui.quit()
