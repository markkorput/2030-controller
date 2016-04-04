#!/usr/bin/env python
import sys

from py2030.controller import Controller
from py2030.utils.color_terminal import ColorTerminal

class Launcher:
    def __init__(self, options = {}):
        # attributes
        self.isSetup = False

        self.options = {}
        self.configure(options)
        self.running = False
        self.stopRequested = False

    def __del__(self):
        self.destroy()

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)
        # TODO; any internal updates needed for the (re-)configuration happen here

    def setup(self):
        self.controller = Controller()
        self.isSetup = True

    def destroy(self):
        self.isSetup = False

    def run(self):
        if not self.isSetup:
            self.setup()

        self.running = True

        ColorTerminal().green('2030 Controller Started')

        try:
            while True:
                if self.stopRequested:
                    break
                self.controller.update()
        except KeyboardInterrupt:
            ColorTerminal().yellow('KeyboardInterrupt. Quitting.')

        self.running = False

    def stop(self):
        self.stopRequested = True

if __name__ == '__main__':
    launcher = Launcher({'argv': sys.argv})
    launcher.run()
