#!/usr/bin/env python
import os
from time import sleep
from datetime import datetime

def launch():
    # python /home/pi/py2030/launcher.py > /home/pi/py2030/log.txt 2>&1 &
    command = './launcher.py > ./log.txt 2>&1'
    print 'Launching py2030 with command:', command
    os.system(command)

if __name__ == '__main__':
    py2030_path = os.path.dirname(__file__)
    os.chdir(py2030_path)

    while True:
        f = open('last-alive.txt', 'r')
        content = f.read()
        f.close()

        now = datetime.now()
        try:
            filetime = datetime.strptime(content, '%Y-%m-%d %H:%M:%S')
        except ValueError as err:
            filetime = None

        if not filetime:
            print 'last-alive.txt not found, launching py2030'
            launch()
        else:
            elapsed = (now-filetime).total_seconds()
            if elapsed > 30:
                print 'More than 15 seconds no sign of life from py2030, launching new background process'
                launch()

        sleep(15)
