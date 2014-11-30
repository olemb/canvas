import math
import audio
from audio import FRAME_RATE, BLOCK_SIZE, FRAME_SIZE, FRAMES_PER_BLOCK

class Clip:
    @classmethod
    def from_json(cls, obj):
        return cls(**obj)

    def __init__(self, filename, start=0, y=0, muted=False):
        self.filename = filename
        self.start = start
        self.end = None
        self.y = 0
        self.muted = muted
        self.recording = False

        self.start_block = None
        self.end_block = None

        self.audio = None

        self._load()

    def _load(self):
        with audio.open_wavefile(self.filename, 'rb') as infile:
            self.end = self.start + (infile.getnframes() / FRAME_RATE)

            frames_per_block = BLOCK_SIZE / FRAME_SIZE
            abs_start_frame = math.floor(self.start * FRAME_RATE)
            
            # Start frame within buffer.
            start_frame = abs_start_frame % FRAMES_PER_BLOCK
            start_frame = int(start_frame)

            end_frame = start_frame + infile.getnframes()
            num_blocks = math.ceil(end_frame / BLOCK_SIZE)

            self.audio = bytearray(num_blocks * BLOCK_SIZE)
            i = start_frame * FRAME_SIZE
            while True:
                block = infile.readframes(1024)
                if not block:
                    break
                self.audio[i:i + len(block)] = block

            self.start_block = abs_start_frame // FRAMES_PER_BLOCK
            self.end_block = self.start_block + num_blocks

            
    def get_block(self, pos):
        if self.start_block <= pos < self.end_block:
            return self.audio[pos * BLOCK_SIZE:(pos + 1) * BLOCK_SIZE]
        else:
            return None

if __name__ == '__main__':
    out = audio.open_output()

    clips = [
        Clip('clips/a.wav', start=0),
        Clip('clips/b.wav', start=0),
        Clip('clips/c.wav', start=0),
    ]

    for pos in range(1000):
        block = audio.add_blocks(clip.get_block(pos) for clip in clips)
        out.write(block)
