from py2030.outputs.output import Output
from py2030.utils.color_terminal import ColorTerminal
from py2030.utils.event import Event
from py2030.interface import Interface

import json, socket

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
        self.verbose = False
        self.host_cache = None

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
        reconnect = False

        # new host or port configs? We need to reconnect, but only if we're running
        if self.connected:
            if 'hostname' in options and self.host() != self.client.client_address[0]:
                reconnect = True
                self.host_cache = None

            if 'ip' in options and self.host() != self.client.client_address[0]:
                reconnect = True
                self.host_cache = None

            # also check for port change. if both host and port changed,
            # restart already happened and self.client.client_address should have the new port
            if 'port' in options and self.port() != self.client.client_address[1]:
                reconnect = True

        if 'verbose' in options:
            self.verbose = options['verbose']

        if reconnect:
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

    def hostname(self):
        return self.options['hostname'] if 'hostname' in self.options else None

    def host(self):
        if self.host_cache:
            return self.host_cache

        if not 'ip' in self.options and 'hostname' in self.options:
            try:
                self.host_cache = socket.gethostbyname(self.options['hostname'])
                return self.host_cache
            except socket.gaierror as err:
                ColorTerminal().red("Could not get IP from hostname: "+self.options['hostname'])
                print err

        # default is localhost
        self.host_cache = self.options['ip'] if 'ip' in self.options else None #'127.0.0.1'
        return self.host_cache

    def client_id(self):
        return self.options['client_id'] if 'client_id' in self.options else None

    def _connect(self):
        if not self.host():
            ColorTerminal().warn("Osc output: no host, can't connect")
            return

        try:
            self.client = OSC.OSCClient()

            if self.host().endswith('.255'):
                ColorTerminal().warn('Osc output detected broadcast IP')
                self.client.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            self.client.connect((self.host(), self.port()))
        except OSC.OSCClientError as err:
            ColorTerminal().fail("OSC connection failure: {0}".format(err))
            return False

        self.connected = True
        self.connectEvent(self)
        ColorTerminal().success("OSC client connected to {0}:{1} (hostname: {2})".format(self.host(), str(self.port()), self.hostname()))
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

    def _sendMessage(self, addr, data=[]):
        msg = OSC.OSCMessage()
        msg.setAddress(addr) # set OSC address

        for item in data:
            msg.append(item)

        if self.connected:
            try:
                self.client.send(msg)
            except OSC.OSCClientError as err:
                pass
            except AttributeError as err:
                ColorTerminal().fail('[osc-out {0}:{1}] error:'.format(self.host(), self.port()))
                print err
                self.stop()

        self.messageEvent(msg, self)

        if self.verbose:
            print '[osc-out {0}:{1}]:'.format(self.host(), self.port()), addr, data

    def trigger(self, event, data):
        self._sendMessage('/'+event, [json.dumps(data)])

    def sendMessage(self, addr, data):
        self._sendMessage(addr, data)
