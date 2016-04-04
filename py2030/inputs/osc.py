from py2030.utils.color_terminal import ColorTerminal
from py2030.utils.event import Event
from py2030.interface import Interface

try:
    from OSC import OSCServer
except ImportError:
    ColorTerminal().warn("importing embedded version of pyOSC library for py2030.inputs.osc")
    from py2030.dependencies.OSC import OSCServer

class Osc:
    def __init__(self, options = {}):
        # attributes
        self.oscServer = None
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
        if self.oscServer == None:
            return

        # we'll enforce a limit to the number of osc requests
        # we'll handle in a single iteration, otherwise we might
        # get stuck in processing an endless stream of data
        limit = 10
        count = 0

        # clear timed_out flag
        self.oscServer.timed_out = False

        # handle all pending requests then return
        while not self.oscServer.timed_out and count < limit:
            self.oscServer.handle_request()
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
            self.oscServer = OSCServer((self.host(), int(self.port())))
            self.oscServer.handle_timeout = self._onTimeout
            self.oscServer.addMsgHandler('/broadcast', self._onBroadcast)
            self.connected = True
            ColorTerminal().success("OSC Server running @ {0}:{1}".format(self.host(), str(self.port())))
        except:
            self.connected = False
            self.oscServer
            ColorTerminal().fail("OSC Server could not start @ {0}:{1}".format(self.host(), str(self.port())))

        if self.connected:
            self.connectEvent(self)

    def _disconnect(self):
        if hasattr(self, 'oscServer') and self.oscServer:
            self.oscServer.close()
            self.connected = False
            self.oscServer = None
            self.disconnectEvent(self)
            ColorTerminal().success('OSC Server stopped')

    def _onBroadcast(self, addr, tags, data, client_address):
        # print('got broadcast, data:', data)
        if len(data) < 1:
            ColorTerminal().warn('Got broadcast OSC message without content')
            content = None
        else:
            content = data[0]

        self.interface.broadcasts.create({'data': content})

    def _onTimeout(self):
        if hasattr(self, 'oscServer') and self.oscServer:
            self.oscServer.timed_out = True
