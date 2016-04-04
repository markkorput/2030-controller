from py2030.utils.color_terminal import ColorTerminal
from py2030.utils.event import Event
from py2030.interface import Interface

try:
    import OSC
except ImportError:
    ColorTerminal().warn("importing embedded version of pyOSC library for py2030.outputs.osc")
    import py2030.dependencies.OSC as OSC

class Osc:
    def __init__(self, options = {}):
        # attributes
        self.client = None
        self.connected = False
        self.running = False

        # events
        self.connectEvent = Event()
        self.disconnectEvent = Event()
        self.messageEvent = Event()

        # default config
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
        # we might need the overwritten options
        previous_options = self.options
        # overwrite/update configuration
        self.options = dict(previous_options.items() + options.items())

        # new host or port configs? We need to reconnect, but only if we're running
        if ('host' in options or 'port' in options) and self.connected:
            self.stop()
            self.start()

        # new manager? register callback
        if 'interface' in options:
            # unregister previous callback
            if 'interface' in previous_options and previous_options['interface']:
                previous_options['interface'].broadcasts.newModelEvent -= self._onNewBroadcast

            # register callback new callback
            if options['interface']: # could also be None if caller is UNsetting the manager
                options['interface'].broadcasts.newModelEvent += self._onNewBroadcast

    def start(self):
        if self._connect():
            self.running = True

    def stop(self):
        self._disconnect()
        self.running = False

    def port(self):
        # default is 8080
        return int(self.options['port']) if 'port' in self.options else 8080

    def host(self):
        # default is localhost
        return self.options['host'] if 'host' in self.options else '127.0.0.1'

    def _connect(self):
        try:
            self.client = OSC.OSCClient()
            self.client.connect((self.host(), self.port()))
        except OSC.OSCClientError as err:
            ColorTerminal().error("OSC connection failure: {0}".format(err))
            return False

        self.connected = True
        self.connectEvent(self)
        ColorTerminal().success("OSC client connected to " + self.host() + ':' + str(self.port()))
        return True

    def _disconnect(self):
        if not hasattr(self, 'client') or not self.client:
            return False
        self.client.close()
        self.client = None
        self.connected = False
        self.disconnectEvent(self)
        ColorTerminal().success("OSC client closed")
        return True

    # callback, called when manager gets a new frame of mocap data
    def _onNewBroadcast(self, model, collection):
        self._sendMessage('/broadcast', model.get('data'))

    def _sendMessage(self, tag, content):
        msg = OSC.OSCMessage()
        msg.setAddress(tag) # set OSC address
        if content:
            msg.append(content)

        try:
            self.client.send(msg)
        except OSC.OSCClientError as err:
            pass
            # ColorTerminal().warn("OSC failure: {0}".format(err))
            # no need to call connect again on the client, it will automatically
            # try to connect when we send the next message

        self.messageEvent(msg, self)
