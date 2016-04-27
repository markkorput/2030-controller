#!/usr/bin/env python
from py2030.utils.color_terminal import ColorTerminal
from py2030.app import App

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
        self.app = App({'profile': options.profile})
        ColorTerminal().green('py2030 App instance started with profile: ' + self.app.profile)

    def destroy(self):
        self.app.destroy()

    def update(self):
        self.app.update()

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-p', '--profile', dest='profile', default="client")
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

    launcher = Launcher({'profile': options.profile})

    try:
        while True:
            launcher.update()
    except KeyboardInterrupt:
        ColorTerminal().yellow('KeyboardInterrupt. Quitting.')

    launcher.destroy()
