#!/usr/bin/env python3
import sys
from package.audio import open_output, add_blocks, SECONDS_PER_BLOCK
from package.clips import Clip

def main():
    out = open_output()

    clips = [
        Clip('clips/a.wav', start=0),
        Clip('clips/a.wav', start=1.8),
        # Clip('clips/b.wav', start=0),
        # Clip('clips/c.wav', start=1),
    ]

    for pos in range(10000):
        print('{:.2}'.format(pos * SECONDS_PER_BLOCK))
        block = add_blocks(clip.get_block(pos) for clip in clips)
        out.write(block)

main()
