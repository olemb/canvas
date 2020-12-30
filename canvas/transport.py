import os
import threading
from . import audio
from .audio import BLOCKS_PER_SECOND, SECONDS_PER_BLOCK, SILENCE
from .audio import sum_blocks
from .clips import Clip, save_mix
from .filenames import make_filename
from .savefile import read_savefile, write_savefile


class Transport:
    def __init__(self, dirname=None):
        self.dirname = dirname
        self.savefilename = os.path.join(dirname, 'clips.json')
        self.clipdir = os.path.join(dirname, 'clips')

        self.clips = []
        self.y = 0.9

        self.solo = False
        self.mode = 'stopped'

        self._sync_event = threading.Event()

        self.block_pos = 0

        if not os.path.exists(self.clipdir):
            # Create clipdir (and dirname)
            os.makedirs(self.clipdir)

        self.audio = audio.Stream(self._audio_callback)
        self.play_ahead = self.audio.play_ahead
        self.audio.start()

    @property
    def recording(self):
        return self.mode == 'recording'

    @property
    def playing(self):
        return self.mode != 'stopped'

    def _get_block(self, pos):
        if self.solo:
            clips = (clip for clip in self.clips
                     if clip.selected)
        else:
            clips = (clip for clip in self.clips
                     if not clip.muted)

        return sum_blocks(clip.get_block(pos) for clip in clips)

    def _sync(self):
        # TODO: timeout.
        self._sync_event.clear()
        self._sync_event.wait()

    def _audio_callback(self, inblock):
        self._sync_event.set()

        if self.playing:
            outblock = self._get_block(self.block_pos + self.play_ahead)
            self.block_pos += 1
        else:
            outblock = SILENCE

        if self.recording:
            self._outfile.writeframes(inblock)
            self._record_clip.length += SECONDS_PER_BLOCK

        return outblock

    def deselect_all(self):
        for clip in self.clips:
            clip.selected = False

    def mute_or_unmute_selection(self):
        selected_clips = [clip for clip in self.clips if clip.selected]

        if any(clip for clip in selected_clips if not clip.muted):
            mute_clips = True
        else:
            mute_clips = False

        for clip in selected_clips:
            clip.muted = mute_clips

    @property
    def pos(self):
        return self.block_pos * SECONDS_PER_BLOCK

    @pos.setter
    def pos(self, pos):
        self.stop_recording()
        self.block_pos = max(0, round(pos * BLOCKS_PER_SECOND))

    def start_recording(self):
        self.stop_recording()

        filename = make_filename(self.clipdir)
        self.deselect_all()
        clip = Clip(filename, start=self.pos, y=self.y, load=False)
        clip.selected = True
        clip.recording = True
        self.clips.append(clip)
        self._record_clip = clip
        self._outfile = audio.open_wavefile(clip.filename, 'wb')
        self.mode = 'recording'
        self._sync()

    def stop_recording(self):
        if self.mode == 'recording':
            self.mode = 'playing'
            self._sync()

            self._outfile.close()
            self._record_clip.load()

    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

        return self.recording

    def play(self):
        self.stop_recording()
        self.mode = 'playing'
        self._sync()

    def stop(self):
        self.stop_recording()
        self.mode = 'stopped'
        self._sync()

    def toggle_playback(self):
        if self.mode != 'stopped':
            self.stop()
        else:
            self.play()

        return self.playing

    def delete(self):
        self.stop_recording()
        keep = []
        for clip in self.clips:
            if clip.selected:
                clip.delete()
            else:
                keep.append(clip)

        self.clips = keep

    def select_next(self, reverse=False):
        if len(self.clips) == 0:
            return

        # Get first selected clip.
        try:
            i = min([i for i, c in enumerate(self.clips) if c.selected])
        except ValueError:
            # No selected clips.
            i = 0
        else:
            if reverse:
                i -= 1
            else:
                i += 1

        self.deselect_all()
        self.clips[i % len(self.clips)].selected = True

    def load(self):
        self.clips = read_savefile(self.savefilename, self.clipdir)

    def save(self):
        write_savefile(self.savefilename, self.clips)

    def save_mix(self, filename=None):
        if filename is None:
            filename = os.path.join(self.dirname, 'mix.wav')
        save_mix(filename, self.clips)

    def close(self):
        self.audio.stop()
