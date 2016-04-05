#!/usr/bin/env python
import sys

from py2030.controller import Controller
from py2030.client import Client
from py2030.utils.color_terminal import ColorTerminal

class Launcher:
    def __init__(self, options = {}):
        # attributes
        self.isSetup = False
        self.running = False
        self.stopRequested = False

        # configuration
        self.options = {}
        self.configure(options)

    def __del__(self):
        self.destroy()

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)
        # TODO; any internal updates needed for the (re-)configuration happen here

    def setup(self):
        if self.isClient():
            self.client = Client()
            ColorTerminal().green('2030 Client Started')

        if self.isController():
            self.controller = Controller()
            ColorTerminal().green('2030 Controller Started')

        self.isSetup = True

    def destroy(self):
        self.isSetup = False

    def isClient(self):
        if 'argv' in self.options:
            for arg in self.options['argv']:
                if arg == '-c' or arg == '--client':
                    return True
        return False

    def isController(self):
        return not self.isClient()

    def run(self):
        if not self.isSetup:
            self.setup()

        self.running = True

        try:
            while True:
                if self.stopRequested: break
                if self.isClient(): self.client.update()
                if self.isController(): self.controller.update()

        except KeyboardInterrupt:
            ColorTerminal().yellow('KeyboardInterrupt. Quitting.')

        self.running = False

    def stop(self):
        self.stopRequested = True

if __name__ == '__main__':
    launcher = Launcher({'argv': sys.argv})
    launcher.run()
