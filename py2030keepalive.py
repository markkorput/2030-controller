#!/usr/bin/env python
import os
from datetime import datetime

if __name__ == '__main__':
    py2030_path = os.path.dirname(__file__)
    os.chdir(py2030_path)

    try:
        while True:
            # python /home/pi/py2030/launcher.py > /home/pi/py2030/log.txt 2>&1 &
            command = './launcher.py >> ./log.txt 2>&1'
            print 'Launching py2030 with command:', command
            os.system(command)
    except KeyboardInterrupt:
        print 'KeyboardInterrupt. Quitting.'
