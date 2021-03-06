from py2030.utils.color_terminal import ColorTerminal
from py2030.utils.event import Event
from py2030.interface import Interface
from py2030.utils.osc_broadcast_server import OscBroadcastServer

try:
    from OSC import OSCServer, NoCallbackError
except ImportError:
    ColorTerminal().warn("importing embedded version of pyOSC library for py2030.inputs.osc")
    from py2030.dependencies.OSC import OSCServer, NoCallbackError

import json

class Osc:
    def __init__(self, options = {}):
        # attributes
        self.osc_server = None
        self.connected = False
        self.running = False
        self.verbose = False
        self.osc_map = None

        self.connectEvent = Event()
        self.disconnectEvent = Event()
        self.unknownMessageEvent = Event()

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

        if 'verbose' in options:
            self.verbose = options['verbose']

        if 'osc_map' in options:
            self.osc_map = options['osc_map']

    def start(self):
        if self._connect():
            self.running = True

    def stop(self):
        if self.connected:
            self._disconnect()
        self.running = False

    def update(self):
        if not self.connected:
            return

        # we'll enforce a limit to the number of osc requests
        # we'll handle in a single iteration, otherwise we might
        # get stuck in processing an endless stream of data
        limit = 50
        count = 0

        # clear timed_out flag
        self.osc_server.timed_out = False

        # handle all pending requests then return
        while not self.osc_server.timed_out and count < limit:
            try:
                self.osc_server.handle_request()
                count += 1
            except Exception as exc:
                ColorTerminal().fail("Something went wrong while handling incoming OSC messages:")
                print exc

    def port(self):
        # default is 2030
        return int(self.options['port']) if 'port' in self.options else 2030

    def host(self):
        # default is localhost
        return self.options['ip'] if 'ip' in self.options else '127.0.0.1'

    def shared_port(self):
        return 'shared' in self.options and self.options['shared']

    def _connect(self):
        if self.connected:
            ColorTerminal().warn('py2030.inputs.osc.Osc - Already connected')
            return False

        try:
            # create server instance
            if self.shared_port():
                self.osc_server = OscBroadcastServer((self.host(), self.port()))
            elif self.host().endswith('.255'):
                ColorTerminal().warn('broadcast IP detected, using broadcast server')
                self.osc_server = OscBroadcastServer((self.host(), self.port()))
            else:
                self.osc_server = OSCServer((self.host(), self.port()))
        except Exception as err:
            # something went wrong, cleanup
            self.connected = False
            self.osc_server = None
            # notify
            if self.shared_port():
                ColorTerminal().fail("{0}\nOSC Broadcast Server could not start @ {1}:{2}".format(err, self.host(), str(self.port())))
            else:
                ColorTerminal().fail("{0}\nOSC Server could not start @ {1}:{2}".format(err, self.host(), str(self.port())))
            # abort
            return False

        # register time out callback
        self.osc_server.handle_timeout = self._onTimeout
        # register specific OSC messages callback(s)
        if not self.isForwarder():
            self.osc_server.addMsgHandler('/change', self._onChange) # deprecated
            self.osc_server.addMsgHandler('/join', self._onJoin)
            self.osc_server.addMsgHandler('/ack', self._onAck)
            self.osc_server.addMsgHandler('/event', self._onEvent)
            self.osc_server.addMsgHandler('/clip', self._onClip)
            self.osc_server.addMsgHandler('/effect', self._onEffect)
            self.osc_server.addMsgHandler('/restart', self._onRestart)

            # self.osc_server.addMsgHandler('default', self._onUnknownMessage)
        self.osc_server.addMsgHandler('default', self._onDefault)


        # set internal connected flag
        self.connected = True
        # notify
        self.connectEvent(self)

        if self.osc_server.__class__ == OscBroadcastServer:
            ColorTerminal().success("OSC Broadcast Server running @ {0}:{1}".format(self.host(), str(self.port())))
        else:
            ColorTerminal().success("OSC Server running @ {0}:{1}".format(self.host(), str(self.port())))

        return True

    def _disconnect(self):
        if hasattr(self, 'osc_server') and self.osc_server:
            self.osc_server.close()
            self.connected = False
            self.osc_server = None
            self.disconnectEvent(self)
            ColorTerminal().success('OSC Server stopped')

    def _onChange(self, addr, tags, data, client_address):
        if len(data) < 1:
            ColorTerminal().warn('Got /change OSC message without data')
            return

        if self.verbose:
            print '[osc-in {0}:{1}]'.format(self.host(), self.port()), addr, data, client_address

        self.interface.updates.create(json.loads(data[0]))

    def _onTimeout(self):
        if hasattr(self, 'osc_server') and self.osc_server:
            self.osc_server.timed_out = True

    def _onUnknownMessage(self, addr, tags, data, client_address):
        ColorTerminal().warn('Got unknown OSC Message {0}'.format((addr, tags, data, client_address)))
        self.unknownMessageEvent(addr, tags, data, client_address, self)

    def _onEvent(self, addr, tags, data, client_address):
        if not self.receivesType(addr[1:]): # remove leading slash:
            return

        if self.verbose:
            print '[osc-in {0}:{1}]'.format(self.host(), self.port()), addr, data, client_address

        params = json.loads(data[0])
        self.interface.genericEvent(params)

    def _onEffect(self, addr, tags, data, client_address):
        if not self.receivesType(addr[1:]): # remove leading slash:
            return

        if self.verbose:
            print '[osc-in {0}:{1}]'.format(self.host(), self.port()), addr, data, client_address

        params = json.loads(data[0])
        self.interface.effectEvent(params)

    def _onJoin(self, addr, tags, data, client_address):
        if not self.receivesType(addr[1:]): # remove leading slash:
            return

        if self.verbose:
            print '[osc-in {0}:{1}]'.format(self.host(), self.port()), addr, data, client_address

        params = json.loads(data[0])
        self.interface.joinEvent(params)

    def _onClip(self, addr, tags, data, client_address):
        if not self.receivesType(addr[1:]): # remove leading slash:
            return

        if self.verbose:
            print '[osc-in {0}:{1}]'.format(self.host(), self.port()), addr, data, client_address

        self.interface.clipEvent(data[0])

    def _onAck(self, addr, tags, data, client_address):
        if not self.receivesType(addr[1:]): # remove leading slash:
            return

        if self.verbose:
            print '[osc-in {0}:{1}]'.format(self.host(), self.port()), addr, data, client_address

        self.interface.ackEvent(json.loads(data[0]))

    def receivesType(self, typ):
        return not 'inputs' in self.options or self.options['inputs'].count(typ) > 0

    def isForwarder(self):
        return 'forwarder' in self.options and self.options['forwarder']

    def _onDefault(self, addr, tags, data, client_address):
        # skip touch osc touch-up events
        if len(data) == 1 and data[0] == 0.0:
            return

        if self.verbose:
            print '[osc-in {0}:{1}]'.format(self.host(), self.port()), addr, data, client_address

        if not self.isForwarder():
            if addr.startswith('/hoh/start/'):
                try:
                    no = int(addr.replace('/hoh/start/', ''))
                    self.interface.hohStartEvent(addr.replace('/hoh/start/', ''))
                except ValueError as err:
                    print '[osc-in] invalid hoh start addr:', addr
                return

            if addr.startswith('/hoh/load/'):
                try:
                    no = int(addr.replace('/hoh/load/', ''))
                    self.interface.hohLoadEvent(addr.replace('/hoh/load/', ''))
                except ValueError as err:
                    print '[osc-in] invalid hoh load addr:', addr
                return


            # if addr.startswith('/hoh/play/')
            #     try:
            #         no = int(addr.replace('/hoh/play/', ''))
            #         self.interface.hohPlayEvent(addr.replace('/hoh/play/', ''))
            #     except ValueError as err:
            #         print '[osc-in] invalid hoh play addr:', addr
            if addr == '/hoh/play':
                self.interface.hohPlayEvent()
                return

            if addr == '/hoh/stop':
                self.interface.hohStopEvent()
                return

            if addr == '/hoh/pause':
                self.interface.hohPauseEvent()
                return

            if addr == '/hoh/seek' and len(data) == 1:
                self.interface.hohSeekEvent(data[0])
                return

            if addr.startswith('/hoh/seek/'):
                pos = addr.replace('/hoh/seek/', '')
                self.interface.hohSeekEvent(pos)
                return

            if addr == '/hoh/speed' and len(data) == 2:
                try:
                    speed = int(data[1])
                except ValueError as err:
                    print '[osc-in] got invalid speed value for /hoh/speed:', data[1]
                    return

                self.interface.hohSpeedEvent(str(data[0]), speed)
                return

            if addr.startswith('/hoh/speed/'):
                values = addr.replace('/hoh/speed/', '').split('/')
                if len(values) != 2:
                    print "could not extract two params from: ", addr
                    return

                try:
                    speed = int(values[1])
                except ValueError as err:
                    print '[osc-in] got invalid speed value for /hoh/speed:', addr
                    return
                self.interface.hohSpeedEvent(values[0], speed)

        # print 'py2030.inputs.Osc._forwardOscMessage with', addr, tags, data, client_address
        # ColorTerminal().warn('Got unknown OSC Message {0}'.format((addr, tags, data, client_address)))
        # self.unknownMessageEvent(addr, tags, data, client_address, self)

        if self.osc_map:
            if addr == '-none-':
                print ('fitlered -none- message')
                return

            if addr in self.osc_map:
                mapper = self.osc_map[addr]
                if 'forward' in mapper:
                    print '[osc-in] mapped to: ', mapper['forward']
                    self.interface.oscMessageEvent(mapper['forward'], tags, data, client_address)

                if data[0] in mapper:
                    addr = mapper[data[0]]
                    if self.verbose:
                        print '[osc-in] mapped to: ', addr
                    self.interface.oscMessageEvent(addr, [], [], client_address)
                    return

        self.interface.oscMessageEvent(addr, tags, data, client_address)

    def _onRestart(self, addr, tags, data, client_address):
        if not self.receivesType(addr[1:]):
            return

        if self.verbose:
            print '[osc-in {0}:{1}]'.format(self.host(), self.port()), addr, data, client_address

        self.interface.restartEvent()
