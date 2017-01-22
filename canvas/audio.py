import sys
if sys.version_info.major < 3:
    sys.exit('Requires Python 3')

import wave
import atexit
import audioop
import pyaudio
from pyaudio import PyAudio

pa = None

BLOCK_SIZE = 4096

FRAME_RATE = 44100
SAMPLE_WIDTH = 2
NUM_CHANNELS = 2
FRAME_SIZE = SAMPLE_WIDTH * NUM_CHANNELS
SILENCE = b'\x00' * BLOCK_SIZE

# Todo: not sure if these are correct.
FRAMES_PER_BLOCK = int(BLOCK_SIZE / FRAME_SIZE)

BYTES_PER_SECOND = FRAME_RATE * FRAME_SIZE
SECONDS_PER_BYTE = 1 / BYTES_PER_SECOND
SECONDS_PER_BLOCK = BLOCK_SIZE * SECONDS_PER_BYTE
BLOCKS_PER_SECOND = 1 / SECONDS_PER_BLOCK

PA_AUDIO_FORMAT = dict(format=pyaudio.paInt16,
                       channels=NUM_CHANNELS,
                       rate=FRAME_RATE,
                       frames_per_buffer=FRAMES_PER_BLOCK)

def _pa_init():
    global pa
    if pa is None:
        pa = PyAudio()
        atexit.register(_pa_terminate)


def _pa_terminate():
    global pa
    if pa:
        pa.terminate()
        pa = None


def terminate():
    if pa is not None:
        pa.terminate()


def add_blocks(blocks):
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


class AudioDevice:
    def __init__(self, callback=None):
        _pa_init()

        def callback_wrapper(inblock, frame_count, time_info, status):
            return (callback(inblock), pyaudio.paContinue)

        self.stream = pa.open(input=True,
                              output=True,
                              stream_callback=callback_wrapper,
                              **PA_AUDIO_FORMAT)

        self.latency = self.stream.get_input_latency() \
                       + self.stream.get_output_latency()
        self.play_ahead = int(round(self.latency * BLOCKS_PER_SECOND))
        self.closed = False

    def close(self):
        if not self.closed:
            self.stream.close()
            self.closed = True


def open_wavefile(filename, mode):
    if 'r' in mode:
        return wave.open(filename, mode)
    elif 'w' in mode:
        outfile = wave.open(filename, mode)
        outfile.setnchannels(NUM_CHANNELS)
        outfile.setsampwidth(SAMPLE_WIDTH)
        outfile.setframerate(FRAME_RATE)
        return outfile


def read_wavefile(filename):
    """Read WAV file and return all data as a byte string."""
    with open_wave(filename, 'r') as infile:
        return infile.readframes(infile.getnframes())
