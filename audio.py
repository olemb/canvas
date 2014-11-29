import wave
import pyaudio
from pyaudio import PyAudio

pa = PyAudio()

AUDIO_FORMAT = dict(format=pyaudio.paInt16, channels=2, rate=44100)

def open_input():
    self.stream = pa.open(input=True, **AUDIO_FORMAT)

def open_output():
    self.stream = pa.open(output=True, **AUDIO_FORMAT)

def read_wave(filename):
    """Read WAV file and return all data as a byte string."""
    with wave.open(filename, 'r') as infile:
        return infile.readframes(infile.getnframes())

def open_wave_outfile():
    outfile = wave.open(self.filename, 'w')
    outfile.setnchannels(2)
    outfile.setsampwidth(2)
    outfile.setframerate(44100)  # Todo: why 2 here?
