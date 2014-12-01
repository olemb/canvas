import math
import audio
from audio import FRAME_RATE, BLOCK_SIZE, FRAME_SIZE, FRAMES_PER_BLOCK
from audio import BLOCKS_PER_SECOND

def _allocate_buffer(start, nframes):
    # Start padding in frames.
    start_padding = math.floor((start * FRAME_RATE) % 1)
    total_nframes = (start_padding + nframes)
    num_blocks = total_nframes / FRAMES_PER_BLOCK
    if num_blocks % 1:
        num_blocks += 1
    num_blocks = int(num_blocks)

    return {'length': nframes / FRAME_RATE,
            'buffer': bytearray(num_blocks * BLOCK_SIZE),
            'start_byte': start_padding * FRAME_SIZE}

class Clip:
    @classmethod
    def from_json(cls, obj):
        return cls(**obj)

    def __init__(self, filename, start=0, y=0, muted=False):
        self.filename = filename
        self.start = start
        self.length = None
        self.y = 0
        self.muted = muted
        self.recording = False

        self.start_block = None
        self.num_blocks = None

        self.audio = None

        self._load()

    def _load(self):
        with audio.open_wavefile(self.filename, 'rb') as infile:
            nframes = infile.getnframes()
            values = _allocate_buffer(self.start, nframes)

            self.audio = values['buffer']
            
            bytepos = values['start_byte']
            read_size = 1024
            while True:
                data = infile.readframes(read_size)
                if not data:
                    break
                self.audio[bytepos:bytepos+len(data)] = data
                bytepos += len(data)

            self.length = nframes * FRAME_RATE
            self.start_block = int(self.start * BLOCKS_PER_SECOND)
            self.num_blocks = int(len(self.audio) / BLOCK_SIZE)
            
    def get_block(self, pos):
        pos -= self.start_block
        if 0 <= pos < self.length:
            return self.audio[pos * BLOCK_SIZE:(pos + 1) * BLOCK_SIZE]
        else:
            return None

if __name__ == '__main__':
    from audio import SECONDS_PER_BLOCK

    out = audio.open_output()

    clips = [
        Clip('clips/a.wav', start=0),
        Clip('clips/a.wav', start=1.8),
        # Clip('clips/b.wav', start=0),
        # Clip('clips/c.wav', start=1),
    ]

    for pos in range(10000):
        print(pos * SECONDS_PER_BLOCK)
        block = audio.add_blocks(clip.get_block(pos) for clip in clips)
        out.write(block)
