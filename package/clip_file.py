import os
import json
from .clips import Clip

def read_clip_file(filename):
    dirname = os.path.dirname(os.path.abspath(filename))
    valid_arguments = {'filename', 'start', 'x', 'muted'}

    clips = []

    with open(filename) as infile:
        for fclip in json.load(infile).get('clips', ()):
            if not 'filename' in fclip:
                continue

            fclip['filename'] = os.path.join(dirname, fclip['filename'])

            fclip = {k: v for k, v in fclip.items() if k in valid_arguments}
            clips.append(Clip(load=False, **fclip))

    return clips
