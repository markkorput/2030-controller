#!/usr/bin/env python

# Add project path to system's python path,
# so we can find and import the pymocap package
import os, sys

thisdir = os.path.dirname(__file__)
projectdir = os.path.abspath(os.path.join(thisdir, '..'))

if projectdir not in sys.path:
  sys.path.insert(0, projectdir)

if __name__ == '__main__':
    import subprocess
    os.chdir(thisdir)
    subprocess.call(['python', '-m', 'unittest', 'discover'])

class EventLog:
    def __init__(self, event):
        self.event = event
        self.log = []
        self.event += self.onEvent
        self.count = 0

    def onEvent(self, *args):
        self.log.append(args)
        self.count += 1

    def __getitem__(self, idx):
        return self.log[idx]
