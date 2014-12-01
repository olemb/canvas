from threading import Thread, Event
from . import audio
from .audio import BLOCKS_PER_SECOND, SILENCE, add_blocks

class ClipThread:
    def __enter__(self):
        return self

    def __exit__(self, *_, **__):
        self.stop()
        return False

class ClipRecorder(ClipThread):
    def __init__(self, filename):
        self.filename = filename
        self.stream = audio.open_input()
        self.stop_event = None
        self.stopped = False
        self.size = 0
        self.latency = self.stream.get_input_latency()

        self.outfile = audio.open_wavefile(self.filename, 'wb')

        self.thread = Thread(target=self._main, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event = Event()
        self.stop_event.wait()

    def _main(self):
        while not self.stop_event:
            block = self.stream.read(1024)
            self.size += len(block)
            self.outfile.writeframes(block)
        self.stream.close()
        self.outfile.close()
        self.stop_event.set()
        self.stopped = True

    def read(self):
        """Read file and return as a byte string."""
        return audio.read_wavefile(self.filename)

    def __repr__(self):
        return '<WAV writer {}, {:.2} seconds>'.format(self.filename,
                                                       self.size / (2*2*44100))


class ClipPlayer(ClipThread):
    # Todo: should pos be in seconds or blocks?
    # (Blocks will be used internally.)
    def __init__(self, clips=None, pos=0):
        if clips is None:
            self.clips = []
        else:
            self.clips = clips
        self.pos = pos
        self.stream = audio.open_output()
        self.stop_event = None
        self.stopped = False
        self.paused = False

        self.latency = self.stream.get_output_latency()
        self.play_ahead = round(self.latency * BLOCKS_PER_SECOND)

        self.thread = Thread(target=self._main, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event = Event()
        self.stop_event.wait()

    def _main(self):
        while not self.stop_event:
            pos = self.pos + self.play_ahead
            if self.paused:
                out.write(SILENCE)
            else:
                block = add_blocks(clip.get_block(pos) for clip in self.clips)
                self.stream.write(block)

            self.pos += 1

        self.stream.close()
        self.stop_event.set()
        self.stopped = True    


class Transport:
    def __init__(self):
        self.clips = []
        self.pos = 0  # Position (in seconds)
        self.y = 0.9

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

    def delete(self):
        # Todo: handle deleting recording clip.
        keep = []
        for clip in self.clips:
            if clip.selected:
                clip.deleted = clip
            else:
                keep.append(clip)

        self.clips = keep

