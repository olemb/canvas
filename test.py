#!/usr/bin/env python3
from package.gui import GUI

from package.clips import Clip

CLIPS = [
    Clip('', start=1, length=10, y=0.5, load=False),
    # Clip('', start=1.2, length=22, y=0.53, load=False),
    # Clip('', start=0.5, length=0, y=0.55, load=False),
]

gui = GUI()
gui.transport.clips = CLIPS
gui.run()
