#!/usr/bin/env python
import sys

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
            from py2030.client import Client
            self.client = Client()
            self._update_children.append(self.client)
            ColorTerminal().green('2030 Client Started')

        if self.do_controller():
            from py2030.controller import Controller
            self.controller = Controller()
            self._update_children.append(self.controller)
            ColorTerminal().green('2030 Controller Started')

    def do_client(self):
        return 'client' in self.options and self.options['client']

    def do_controller(self):
        return not self.do_client()

    def update(self):
        for child in self._update_children:
            child.update()

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-c', '--client', dest='client', action="store_true", default=False)
    parser.add_option('--install', dest='install', action="store_true", default=False)
    parser.add_option('--bootstrap', dest='bootstrap', action="store_true", default=False)
    options, remainder = parser.parse_args()
    del OptionParser

    if options.install:
        ColorTerminal().red('--install not implemented yet')

    if options.bootstrap:
        ColorTerminal().red('--bootstrap not implemented yet')

    if options.install or options.bootstrap:
        # we're done
        exit(0)

    launcher = Launcher({'client': options.client})

    try:
        while True:
            launcher.update()
    except KeyboardInterrupt:
        ColorTerminal().yellow('KeyboardInterrupt. Quitting.')
