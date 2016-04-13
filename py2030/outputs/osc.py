from py2030.outputs.output import Output
from py2030.utils.color_terminal import ColorTerminal
from py2030.utils.event import Event
from py2030.interface import Interface

import json

try:
    import OSC
except ImportError:
    ColorTerminal().warn("importing embedded version of pyOSC library for py2030.outputs.osc")
    import py2030.dependencies.OSC as OSC

class Osc(Output):
    def __init__(self, options = {}):
        # attributes
        self.client = None
        self.connected = False
        self.running = False

        # events
        self.connectEvent = Event()
        self.disconnectEvent = Event()
        self.messageEvent = Event()

        Output.__init__(self, options)

        # autoStart is True by default
        if not 'autoStart' in options or options['autoStart']:
            self.start()

    def __del__(self):
        self.stop()

    def configure(self, options):
        Output.configure(self, options)

        # new host or port configs? We need to reconnect, but only if we're running
        if self.connected:
            if 'host' in options and self.host() != self.client.client_address[0]:
                self.stop()
                self.start()
            # also check for port change. if both host and port changed,
            # restart already happened and self.client.client_address should have the new port
            if 'port' in options and self.port() != self.client.client_address[1]:
                self.stop()
                self.start()

    def start(self):
        if self._connect():
            self.running = True

    def stop(self):
        self._disconnect()
        self.running = False

    def port(self):
        # default is 2030
        return int(self.options['port']) if 'port' in self.options else 2030

    def host(self):
        # default is localhost
        return self.options['host'] if 'host' in self.options else '127.0.0.1'

    def _connect(self):
        try:
            self.client = OSC.OSCClient()
            self.client.connect((self.host(), self.port()))
        except OSC.OSCClientError as err:
            ColorTerminal().fail("OSC connection failure: {0}".format(err))
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

    def output(self, change_model):
        self._sendMessage('/change', [json.dumps(change_model.data)])

    def _sendMessage(self, tag, data=[]):
        msg = OSC.OSCMessage()
        msg.setAddress(tag) # set OSC address

        for item in data:
            msg.append(item)

        if self.connected:
            print('py2030.outputs.osc.Osc sending message: ', tag, data)
            try:
                self.client.send(msg)
            except OSC.OSCClientError as err:
                pass
                # ColorTerminal().warn("OSC failure: {0}".format(err))
                # no need to call connect again on the client, it will automatically
                # try to connect when we send the next message

        self.messageEvent(msg, self)
