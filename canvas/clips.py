import os
import math
from .audio import FRAME_RATE, BLOCK_SIZE, FRAME_SIZE, FRAMES_PER_BLOCK
from .audio import BLOCKS_PER_SECOND, open_wavefile, sum_blocks


def _allocate_buffer(start, nframes):
    # Start padding in frames.
    start_padding = math.floor((start * FRAME_RATE) % 1)
    total_nframes = start_padding + nframes
    num_blocks = total_nframes / FRAMES_PER_BLOCK
    if num_blocks % 1:
        num_blocks += 1
    num_blocks = int(num_blocks)

    return {
        'length': nframes / FRAME_RATE,
        'buffer': bytearray(num_blocks * BLOCK_SIZE),
        'start_byte': start_padding * FRAME_SIZE,
    }


class Clip:
    def __init__(self, filename, start=0, y=0, muted=False, load=True,
                 length=0):
        self.filename = filename
        self.start = start
        self.length = length
        self.y = y
        self.muted = muted
        self.recording = False
        self.selected = False
        self.deleted = False

        self.start_block = 0
        self.num_blocks = 0

        self.audio = None

        if load:
            self.load()

    def load(self):
        with open_wavefile(self.filename, 'rb') as infile:
            nframes = infile.getnframes()
            values = _allocate_buffer(self.start, nframes)

            self.audio = values['buffer']

            bytepos = values['start_byte']
            read_size = 1024
            while True:
                data = infile.readframes(read_size)
                if not data:
                    break
                self.audio[bytepos:bytepos + len(data)] = data
                bytepos += len(data)

            self.length = nframes / FRAME_RATE
            self.start_block = int(self.start * BLOCKS_PER_SECOND)
            self.num_blocks = int(len(self.audio) / BLOCK_SIZE)

    def get_block(self, pos):
        pos -= self.start_block
        if 0 <= pos < self.num_blocks:
            return self.audio[pos * BLOCK_SIZE:(pos + 1) * BLOCK_SIZE]
        else:
            return None

    def delete(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def __repr__(self):
        filename = os.path.basename(self.filename)
        return (
            f'Clip({filename!r}, start={self.start:.2f},'
            f' y={self.y:.2f}, muted={self.muted})'
        )


def get_start_and_end(clips):
    """Get start and end time of a clip list in seconds."""
    if len(clips) == 0:
        return (0, 0)
    else:
        return (
            min(clip.start for clip in clips),
            max(clip.start + clip.length for clip in clips),
        )


def save_mix(filename, clips):
    clips = [clip for clip in clips if not clip.muted]

    start, end = get_start_and_end(clips)
    start_block = math.floor(start * BLOCKS_PER_SECOND)
    end_block = math.ceil(end * BLOCKS_PER_SECOND)

    with open_wavefile(filename, 'wb') as outfile:
        for pos in range(start_block, end_block):
            block = sum_blocks(clip.get_block(pos) for clip in clips)
            outfile.writeframes(block)
