import os
from threading import Thread, Event
from . import audio
from .audio import BLOCKS_PER_SECOND, SECONDS_PER_BLOCK, SILENCE
from .audio import BLOCK_SIZE, FRAME_SIZE, add_blocks
from .clips import Clip
from .filenames import make_filename
from .savefile import read_savefile, write_savefile

class ClipThread:
    def __enter__(self):
        return self

    def __exit__(self, *_, **__):
        self.stop()
        return False

class ClipRecorder(ClipThread):
    def __init__(self, clip):
        self.clip = clip
        self.clip.recording = True
        self.audio_in = audio.open_input()
        self.stop_event = None
        self.latency = self.audio_in.get_input_latency()

        self.thread = Thread(target=self._main, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event = Event()
        self.stop_event.wait()

    def _main(self):
        self.outfile = audio.open_wavefile(self.clip.filename, 'wb')

        read_size = int(BLOCK_SIZE / FRAME_SIZE)

        num_blocks = 0
        while not self.stop_event:
            block = self.audio_in.read(read_size)
            num_blocks += 1
            self.clip.length = num_blocks * SECONDS_PER_BLOCK
            self.outfile.writeframes(block)
        self.audio_in.close()
        self.outfile.close()
        self.clip.recording = False
        self.clip.load()
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
        self.audio_out = audio.open_output()
        self.stop_event = None
        self.paused = False

        self.latency = self.audio_out.get_output_latency()
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
                self.audio_out.write(block)

        self.audio_out.close()
        self.stop_event.set()


class Transport:
    def __init__(self, dirname=None):
        self.dirname = dirname
        self.savefilename = os.path.join(dirname, 'clips.json')
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        self.clips = []
        self.y = 0.9

        self.player = None
        self.recorder = None

        self.block_pos = 0

    def deselect_all(self):
        for clip in self.clips:
            clip.selected = False

    @property
    def pos(self):
        return self.block_pos * SECONDS_PER_BLOCK

    @pos.setter
    def pos(self, pos):
        self.stop_recording()
        self.block_pos = max(0, round(pos * BLOCKS_PER_SECOND))

    @property
    def playing(self):
        return self.player is not None

    @property
    def recording(self):
        return self.recorder is not None

    def start_recording(self):
        self.stop_recording()
        if self.recorder is None:
            filename = make_filename(self.dirname)
            clip = Clip(filename, start=self.pos, y=self.y, load=False)
            self.deselect_all()
            clip.selected = True
            self.clips.append(clip)
            self.play()
            self.recorder = ClipRecorder(clip)

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
        self.stop_recording()
        if self.player:
            self.player.stop()
            self.player = None

    def delete(self):
        self.stop_recording()
        # Todo: handle deleting recording clip.
        # Todo: delete file?
        keep = []
        for clip in self.clips:
            if clip.selected:
                clip.deleted = clip
            else:
                keep.append(clip)

        self.clips = keep

    def load(self):
        self.clips = read_savefile(self.savefilename)

    def save(self):
        write_savefile(self.savefilename, self.clips)
