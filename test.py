from package.clip_file import read_clip_file

clips = read_clip_file('test.json')
for clip in clips:
    print(clip)
