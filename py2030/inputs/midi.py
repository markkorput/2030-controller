#!/usr/bin/env python
#
# test_midiin_poll.py
#
"""Shows how to receive MIDI input by polling an input port."""

import logging
import sys
import time

import rtmidi
from rtmidi.midiutil import open_midiport

class MidiTest:
    def __init__(self):
        self.port = None # = sys.argv[1] if len(sys.argv) > 1 else None
        self.midiin = None
        self.setup()

    def setup(self):
        # self.logger = logging.getLogger('test_midiin_poll')
        # logging.basicConfig(level=logging.DEBUG)

        try:
            self.midiin, self.port_name = open_midiport(self.port)
        except (EOFError, KeyboardInterrupt):
            print("Failed to initialize MIDI interface")
            self.midiin = None
            self.port_name = None

        self.time = time.time()

    def __del__(self):
        if self.midiin:
            self.midiin.close_port()
            self.midiin = None

    def update(self):
        if not self.midiin:
            return

        msg = self.midiin.get_message()

        if msg:
            message, deltatime = msg
            self.time += deltatime
            print("[%s] @%0.6f %r" % (self.port_name, deltatime, message))

if __name__ == '__main__':
    mt = MidiTest()

    print("Entering main loop. Press Control-C to exit.")
    try:
        while True:
            mt.update()
            time.sleep(0.01)
    except KeyboardInterrupt:
        print('Keyboard Interrupt')

    del mt
