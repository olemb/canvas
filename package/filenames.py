import os
import random

consonants = 'bcdfghjklmnpqrstvwxz'
vowels = 'aeiouy'

def _make_name():
    chars = []
    for i in range(4):
        chars.append(random.choice(consonants))
        chars.append(random.choice(vowels))
    return ''.join(chars) + '.wav'

def make_filename(dirname):
    while True:
        filename = os.path.join(dirname, _make_name())
        if not os.path.exists(filename):
            return filename
