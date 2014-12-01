from threading import Thread, Event
from . import audio

# print('Input latency: {}'.format(instream.get_input_latency()))
# print('Output latency: {}'.format(outstream.get_output_latency()))

class ClipRecorder:
    def __init__(self, filename):
        self.filename = filename
        self.stream = audio.open_input()
        self._stop_event = None
        self.stopped = False
        self.size = 0
        self.latency = self.stream.get_input_latency()

        self.outfile = audio.open_wavefile(self.filename, 'wb')

        self.thread = Thread(target=self._main, daemon=True)
        self.thread.start()

    def stop(self):
        self._stop_event = Event()
        self._stop_event.wait()

    def _main(self):
        while not self._stop_event:
            block = self.stream.read(1024)
            self.size += len(block)
            self.outfile.writeframes(block)
        self.stream.close()
        self.outfile.close()
        self._stop_event.set()
        self.stopped = True

    def read(self):
        """Read file and return as a byte string."""
        return audio.read_wavefile(self.filename)

    def __repr__(self):
        return '<WAV writer {}, {:.2} seconds>'.format(self.filename,
                                                       self.size / (2*2*44100))



class ClipPlayer:
    def __init__(self, clips):
        self.clips = clips


class Transport:
    def __init__(self):
        self.clips = []
        self.pos = 0  # Position (in seconds)

        self.player = None
        self.recorder = None

    @property
    def playing(self):
        return self.player is not None

    @property
    def recording(self):
        return self.recorder is not None

    def _stop_recording(self):
        if self.recorder is not None:
            self.recorder.stop()
            # Todo: load clip.

    def toggle_play(self):
        if self.playing():
            self.stop()
        else:
            self.play()

    def play(self):
        self._stop_recording()
        if not self.playing:
            self.player = ClipPlayer(self.clips)

    def stop(self):
        self._stop_recording()
        pass

    def record(self, filename):
        self._stop_recording()
        self.recorder = ClipRecorder(filename)

    def goto(self):
        self._stop_recording()
        pass

    def skip(self, n):
        self._stop_recording()
        pass
