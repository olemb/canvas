#!/usr/bin/env python3
import sys
import time
from package import Transport

if __name__ == '__main__':
    t = Transport()
    print('Recording...')
    t.record(sys.argv[1])
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    t.stop()
    print('Stopped.')
