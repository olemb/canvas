import sys
if sys.version_info.major < 3:
    sys.exit('Requires Python 3')

import wave
import atexit
import audioop
import pyaudio
from pyaudio import PyAudio

pa = None

BLOCK_SIZE = 1024

FRAME_RATE = 44100
SAMPLE_WIDTH = 2
NUM_CHANNELS = 2
FRAME_SIZE = SAMPLE_WIDTH * NUM_CHANNELS
SILENCE = b'\x00' * BLOCK_SIZE

# Todo: not sure if these are correct.
FRAMES_PER_BLOCK = BLOCK_SIZE / FRAME_SIZE

BYTES_PER_SECOND = FRAME_RATE * FRAME_SIZE
SECONDS_PER_BYTE = 1 / BYTES_PER_SECOND
SECONDS_PER_BLOCK = BLOCK_SIZE * SECONDS_PER_BYTE
BLOCKS_PER_SECOND = 1 / SECONDS_PER_BLOCK

PA_AUDIO_FORMAT = dict(format=pyaudio.paInt16,
                       channels=NUM_CHANNELS,
                       rate=FRAME_RATE)


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


def open_input():
    _pa_init()
    return pa.open(input=True, **PA_AUDIO_FORMAT)


def open_output():
    _pa_init()
    return pa.open(output=True, **PA_AUDIO_FORMAT)


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
