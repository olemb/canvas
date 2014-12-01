#!/usr/bin/env python3
import sys
import time
import random
# from package.audio import open_output, add_blocks, SECONDS_PER_BLOCK
from package.clips import Clip, save_mix
from package.transport import ClipPlayer
from package.audio import SECONDS_PER_BLOCK

def main():
    clips = [
        Clip('clips/a.wav', start=0.1),
        Clip('clips/a.wav', start=1.8),
        # Clip('clips/b.wav', start=0),
        # Clip('clips/c.wav', start=1),
    ]

    save_mix('out.wav', clips)

    with ClipPlayer(clips, pos=0) as player:
        while True:
            print('{:.2}'.format(player.pos * SECONDS_PER_BLOCK))
            time.sleep(0.2)

main()
