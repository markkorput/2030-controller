from py2030.utils.color_terminal import ColorTerminal
from py2030.utils.event import Event
from py2030.interface import Interface

import json

try:
    from OSC import OSCServer
except ImportError:
    ColorTerminal().warn("importing embedded version of pyOSC library for py2030.inputs.osc")
    from py2030.dependencies.OSC import OSCServer

# import socket
# myip = socket.gethostbyname(socket.gethostname())
# print('my ip: {0}'.format(myip))

class Osc:
    def __init__(self, options = {}):
        # attributes
        self.osc_server = None
        self.connected = False
        self.running = False

        self.connectEvent = Event()
        self.disconnectEvent = Event()

        # default configs
        if not 'interface' in options:
            options['interface'] = Interface.instance()

        # configuration
        self.options = {}
        self.configure(options)

        # autoStart is True by default
        if not 'autoStart' in options or options['autoStart']:
            self.start()

    def __del__(self):
        self.stop()

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)

        if 'interface' in options:
            self.interface = options['interface']

    def start(self):
        if self._connect():
            self.running = True

    def stop(self):
        if self.connected:
            self._disconnect()
        self.running = False

    def update(self):
        if self.osc_server == None:
            return

        # we'll enforce a limit to the number of osc requests
        # we'll handle in a single iteration, otherwise we might
        # get stuck in processing an endless stream of data
        limit = 10
        count = 0

        # clear timed_out flag
        self.osc_server.timed_out = False

        # handle all pending requests then return
        while not self.osc_server.timed_out and count < limit:
            self.osc_server.handle_request()
            count += 1

    def port(self):
        # default is 8080
        return int(self.options['port']) if 'port' in self.options else 8080

    def host(self):
        # default is localhost
        return self.options['host'] if 'host' in self.options else '127.0.0.1'

    def _connect(self):
        if self.connected:
            ColorTerminal().warning('py2030.inputs.osc.Osc - Already connected')
            return

        try:
            # create server instance
            self.osc_server = OSCServer((self.host(), int(self.port())))
            # register time out callback
            self.osc_server.handle_timeout = self._onTimeout
            # register specific OSC messages callback(s)
            self.osc_server.addMsgHandler('/change', self._onChange)
        except:
            # something went wrong, cleanup
            self.connected = False
            self.osc_server = None
            # notify
            ColorTerminal().fail("OSC Server could not start @ {0}:{1}".format(self.host(), str(self.port())))
            # abort
            return

        # set internal connected flag
        self.connected = True
        # notify
        ColorTerminal().success("OSC Server running @ {0}:{1}".format(self.host(), str(self.port())))
        self.connectEvent(self)

    def _disconnect(self):
        if hasattr(self, 'osc_server') and self.osc_server:
            self.osc_server.close()
            self.connected = False
            self.osc_server = None
            self.disconnectEvent(self)
            ColorTerminal().success('OSC Server stopped')

    def _onChange(self, addr, tags, data, client_address):
        print('received /change, data:', data)
        if len(data) < 1:
            ColorTerminal().warn('Got /change OSC message without data')
            return

        self.interface.updates.create(json.loads(data[0]))

    def _onTimeout(self):
        if hasattr(self, 'osc_server') and self.osc_server:
            self.osc_server.timed_out = True
