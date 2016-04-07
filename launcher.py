#!/usr/bin/env python
import sys

from py2030.controller import Controller
from py2030.client import Client
from py2030.utils.color_terminal import ColorTerminal

class Launcher:
    def __init__(self, options = {}):
        # attributes
        self._update_children = []

        # configuration
        self.options = options

        # autoStart is True by default
        if not 'setup' in options or options['setup']:
            self.setup()

    def setup(self):
        if self.do_client():
            self.client = Client()
            self._update_children.append(self.client)
            ColorTerminal().green('2030 Client Started')

        if self.do_controller():
            self.controller = Controller()
            self._update_children.append(self.controller)
            ColorTerminal().green('2030 Controller Started')

    def do_client(self):
        if 'argv' in self.options:
            if '-c' in self.options['argv'] or '--client' in self.options['argv']:
                return True
        return False

    def do_controller(self):
        return not self.do_client()

    def update(self):
        for child in self._update_children:
            child.update()

if __name__ == '__main__':
    launcher = Launcher({'argv': sys.argv})

    try:
        while True:
            launcher.update()
    except KeyboardInterrupt:
        ColorTerminal().yellow('KeyboardInterrupt. Quitting.')
