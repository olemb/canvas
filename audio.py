import wave
import pyaudio
from pyaudio import PyAudio

def get_block_size():
    """Return block size in bytes."""
    return 1024

def get_block_nframes():
    """Return block size in frames."""
    return 256

def _pa_init(self):
    global pa
    if pa is None:
        pa = PyAudio()

AUDIO_FORMAT = dict(format=pyaudio.paInt16, channels=2, rate=44100)

def open_input():
    _pa_init()
    return pa.open(input=True, **AUDIO_FORMAT)

def open_output():
    _pa_init()
    return pa.open(output=True, **AUDIO_FORMAT)

def open_wavefile(filename, mode):
    if 'r' in mode:
        return wave.open(filename, mode)
    elif 'w' in mode:
        outfile = wave.open(filename, mode)
        outfile.setnchannels(2)
        outfile.setsampwidth(2)
        outfile.setframerate(44100)  # Todo: why 2 here?
        return outfile

def read_wavefile(filename):
    """Read WAV file and return all data as a byte string."""
    with open_wave(filename, 'r') as infile:
        return infile.readframes(infile.getnframes())
