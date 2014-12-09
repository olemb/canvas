import os
import random

# Consonants and vowels that are easy to pronounce.
consonants = 'bdfghjklmnprstv'
vowels = 'aiueo'

def random_syllable():
    return random.choice(consonants) + random.choice(vowels)

def _make_name():
    return ''.join(random_syllable() for _ in range(4)) + '.wav'

def make_filename(dirname):
    while True:
        filename = os.path.join(dirname, _make_name())
        if not os.path.exists(filename):
            return filename
