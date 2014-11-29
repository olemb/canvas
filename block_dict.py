"""
Prototype that reads a file into a dictionary of blocks.

Keys in the dictionary are absolute block positions in the
timeline. For example a clip that starts at block 10 will have
keys from 10 and up. This makes it easy to get blocks from all clips
that have a block at the given position:

    block = add_blocks(clip.blocks[pos] for clip in clips
                       if pos in clip.blocks)

Upsides:

1) Lookup is much quicker and easier.

Downsides:

1) Each clip is time-locked (unless you modify the keys).
2) Uses more memory.
3) Clips must padded if they don't start and end at block boundaries.
"""
import audio

nframes = audio.get_block_nframes()

blocks = {}

i = 0
with audio.open_wavefile('out.wav', 'rb') as infile:
    while True:
        block = infile.readframes(nframes)
        if not block:
            break
        blocks[i] = block
        i += 1

print(audio.add_blocks(list(blocks.values())))
print(audio.add_blocks([]))

