import wave
import audioop
import sounddevice


BLOCK_SIZE = 4096

FRAME_RATE = 44100
SAMPLE_WIDTH = 2
NUM_CHANNELS = 2
FRAME_SIZE = SAMPLE_WIDTH * NUM_CHANNELS
SILENCE = b'\x00' * BLOCK_SIZE

# TODO: not sure if these are correct.
FRAMES_PER_BLOCK = int(BLOCK_SIZE / FRAME_SIZE)

BYTES_PER_SECOND = FRAME_RATE * FRAME_SIZE
SECONDS_PER_BYTE = 1 / BYTES_PER_SECOND
SECONDS_PER_BLOCK = BLOCK_SIZE * SECONDS_PER_BYTE
BLOCKS_PER_SECOND = 1 / SECONDS_PER_BLOCK

def sum_blocks(blocks):
    """Return a block where with the sum of the samples on all blocks.

    Takes an interable of blocks (byte strings). If no blocks are passed
    a silent block (all zeroes) will be returned.

    Treats None values as silent blocks.
    """
    blocksum = SILENCE

    for block in blocks:
        if block:
            blocksum = audioop.add(blocksum, block, 2)

    return blocksum


class Stream:
    def __init__(self, callback):
        def callback_wrapper(inblock, outblock, *_):
            outblock[:] = callback(bytes(inblock))

        self.stream = sounddevice.RawStream(
            samplerate=FRAME_RATE,
            channels=2,
            dtype='int16',
            blocksize=FRAMES_PER_BLOCK,
            callback=callback_wrapper,
        )
        self.latency = sum(self.stream.latency)
        self.play_ahead = int(round(self.latency * BLOCKS_PER_SECOND))

    def start(self):
        self.stream.start()

    def stop(self):
        self.stream.stop()


def open_wavefile(filename, mode):
    outfile = wave.open(filename, mode)
    if 'w' in mode:
        outfile.setnchannels(NUM_CHANNELS)
        outfile.setsampwidth(SAMPLE_WIDTH)
        outfile.setframerate(FRAME_RATE)
    return outfile
