#!/usr/bin/env python
from py2030.app import App

class Launcher:
    def __init__(self, options):
        # attributes
        self._update_children = []
        self.running = True

        # configuration
        self.options = options
        self.setup()

    def setup(self):
        self.app = App({'profile': options.profile, 'file': options.file, 'loop': options.loop})

        self.app.setup()

        if self.app.downloader:
            self.app.downloader.newVersionEvent += self._onNewVersion

    def destroy(self):
        self.app.destroy()

    def update(self):
        self.app.update()

    def _onNewVersion(self, version, downloader):
        print '[Launcher] received new version notification: ' + version + ". Restarting!"
        self.running = False

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
            print "Routed IP address {0} to interface {1}".format(ip, interface)
            print "run `netstat -r` to check"
        else:
            print "USAGE: launcher.py --route-ip <ip-address> [<interface>]"

        return

    if options.install:
        print '--install not implemented yet'

    if options.bootstrap:
        print '--bootstrap not implemented yet'

    if options.install or options.bootstrap:
        # we're done
        exit(0)

    launcher = Launcher(options)

    try:
        while launcher.running:
            launcher.update()
    except KeyboardInterrupt:
        print 'KeyboardInterrupt. Quitting.'

    launcher.destroy()

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-p', '--profile', dest='profile', default="client")
    # parser.add_option('-c', '--client', dest='client', action="store_true", default=False)
    parser.add_option('-f', '--file', dest='file', default=None)
    parser.add_option('-l', '--loop', dest='loop', action="store_true", default=False)
    parser.add_option('-t', '--threaded', dest='threaded', action="store_true", default=False)
    parser.add_option('--install', dest='install', action="store_true", default=False)
    parser.add_option('--bootstrap', dest='bootstrap', action="store_true", default=False)
    parser.add_option('--route-ip', dest="route_ip", action="store_true", help="Route IP address (default: the controller profile's osc_out_ip value from the config file) to specific interface (default: en0)", default=None)
    options, args = parser.parse_args()
    del OptionParser

    main(options, args)
