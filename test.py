from package.clip_file import read_clip_file

clips = read_clip_file('testclips/test.json')
for clip in clips:
    clip.load()
    print(clip)
