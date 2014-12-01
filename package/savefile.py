import os
import json
from .clips import Clip

def read_savefile(filename):
    dirname = os.path.dirname(os.path.abspath(filename))

    if not os.path.exists(filename):
        return []

    valid_arguments = {'filename', 'start', 'x', 'muted'}
    clips = []

    with open(filename) as infile:
        for fclip in json.load(infile).get('clips', ()):
            if not 'filename' in fclip:
                continue
                
            fclip['filename'] = os.path.join(dirname, fclip['filename'])
            fclip = {k: v for k, v in fclip.items() if k in valid_arguments}
            clips.append(Clip(load=True, **fclip))

    return clips

def write_savefile(filename, clips):
    fclips = [
        {
            'filename': os.path.basename(clip.filename),
            'start': clip.start,
            'y': clip.y,
            'muted': clip.muted,
        }
        for clip in clips]

    with open(filename, 'wt') as outfile:
        json.dump({'clips': fclips}, outfile)

