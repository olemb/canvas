from threading import Thread, Event
from . import audio
from .audio import BLOCKS_PER_SECOND, SECONDS_PER_BLOCK, SILENCE, add_blocks

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

    def read(self):
        """Read file and return as a byte string."""
        return audio.read_wavefile(self.filename)

    def __repr__(self):
        return '<WAV writer {}, {:.2} seconds>'.format(self.filename,
                                                       self.size / (2*2*44100))


class ClipPlayer(ClipThread):
    # Todo: should pos be in seconds or blocks?
    # (Blocks will be used internally.)
    def __init__(self, transport):
        self.transport = transport
        self.stream = audio.open_output()
        self.stop_event = None
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
            pos = self.transport.block_pos + self.play_ahead
            self.transport.block_pos += 1
            if self.paused:
                out.write(SILENCE)
            else:
                block = add_blocks(clip.get_block(pos) \
                                   for clip in self.transport.clips)
                self.stream.write(block)

        self.stream.close()
        self.stop_event.set()


class Transport:
    def __init__(self):
        self.clips = []
        self.y = 0.9

        self.player = None
        self.recorder = None

        self.block_pos = 0

    @property
    def pos(self):
        return self.block_pos * SECONDS_PER_BLOCK

    @pos.setter
    def pos(self, pos):
        self.block_pos = max(0, round(pos * BLOCKS_PER_SECOND))

    @property
    def playing(self):
        return self.player is not None

    @property
    def recording(self):
        return self.recorder is not None

    def start_recording(self):
        # if self.recorder is None:
        #   self.recorder = ClipRecorder(clip)
        pass

    def stop_recording(self):
        if self.recorder is not None:
            self.recorder.stop()
            # Todo: load clip.
            # self.recorder.clip.load()
            self.recorder = None

    def play(self):
        if not self.player:
            self.player = ClipPlayer(self)

    def stop(self):
        if self.player:
            self.player.stop()
            self.player = None

    def record(self, filename):
        self._stop_recording()
        self.recorder = ClipRecorder(filename)

    def delete(self):
        # Todo: handle deleting recording clip.
        # Todo: delete file?
        keep = []
        for clip in self.clips:
            if clip.selected:
                clip.deleted = clip
            else:
                keep.append(clip)

        self.clips = keep
