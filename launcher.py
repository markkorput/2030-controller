#!/usr/bin/env python
from py2030.utils.color_terminal import ColorTerminal
from py2030.app import App

class Launcher:
    def __init__(self, options = {}):
        # attributes
        self._update_children = []

        # configuration
        self.options = options
        self.setup()

    def setup(self):
        self.app = App({'profile': options.profile, 'file': options.file})
        # ColorTerminal().green('py2030 App instance started with profile: ' + self.app.profile)

    def destroy(self):
        self.app.destroy()

    def update(self):
        self.app.update()

def main(options, args):
    if options.route_ip:
        from py2030.config_file import ConfigFile
        cfile = ConfigFile.instance()
        cfile.load()
        ip = args[0] if len(args) > 0 else None
        interface = args[1] if len(args) > 1 else 'en0'

        if ip:
            import os
            os.system('sudo route -nv add -net {0} -interface {1}'.format(ip, interface))
            ColorTerminal().success("Routed IP address {0} to interface {1}".format(ip, interface))
            ColorTerminal().success("run `netstat -r` to check")
        else:
            ColorTerminal().fail("USAGE: launcher.py --route-ip <ip-address> [<interface>]")

        return

    if options.install:
        ColorTerminal().red('--install not implemented yet')

    if options.bootstrap:
        ColorTerminal().red('--bootstrap not implemented yet')

    if options.install or options.bootstrap:
        # we're done
        exit(0)

    launcher = Launcher(options)

    try:
        while True:
            launcher.update()
    except KeyboardInterrupt:
        ColorTerminal().yellow('KeyboardInterrupt. Quitting.')

    launcher.destroy()

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-p', '--profile', dest='profile', default="client")
    # parser.add_option('-c', '--client', dest='client', action="store_true", default=False)
    parser.add_option('-f', '--file', dest='file', default=None)
    parser.add_option('--install', dest='install', action="store_true", default=False)
    parser.add_option('--bootstrap', dest='bootstrap', action="store_true", default=False)
    parser.add_option('--route-ip', dest="route_ip", action="store_true", help="Route IP address (default: the controller profile's osc_out_ip value from the config file) to specific interface (default: en0)", default=None)
    options, args = parser.parse_args()
    del OptionParser

    main(options, args)
