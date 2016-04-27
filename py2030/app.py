from py2030.utils.color_terminal import ColorTerminal
from py2030.interface import Interface
from py2030.interval_broadcast import IntervalBroadcast
from py2030.outputs.osc import Osc
from py2030.config_file import ConfigFile
from py2030.config_file_monitor import ConfigFileMonitor
from py2030.inputs.midi import MidiEffectInput
from py2030.http_server import HttpServer
from py2030.config_broadcaster import ConfigBroadcaster

class App:
    def __init__(self, options = {}):
        # attributes
        self.interface = Interface.instance() # use global interface singleton instance
        self.interval_broadcast = None
        self.broadcast_osc_output = None
        self.config_file = None #ConfigFile.instance()
        self.config_file_monitor = None
        self.config_file_monitor = None # ConfigFileMonitor(self.config_file, start=False)
        self.midi_effect_input = None # MidiEffectInput()
        self.http_server = None
        self.config_broadcaster = None # ConfigBroadcaster()

        # configuration
        self.options = {}
        self.configure(options)

        # autoStart is True by default
        if not 'autoStart' in options or options['autoStart']:
            self.setup()

    def __del__(self):
        self.destroy()

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)

    def setup(self):
        return
        self.config_file.load()
        # apply config
        self.applyConfig(self.config_file.data)
        # start monitoring for file changes
        self.config_file.dataChangeEvent += self._onConfigDataChange
        self.config_file_monitor.start()

    def _onConfigDataChange(self, data, config_file):
        ColorTerminal().yellow('config change: {0}'.format(data))
        self.applyConfig(data)

    def destroy(self):
        if self.broadcast_osc_output:
            self.broadcast_osc_output.stop()
            self.broadcast_osc_output = None

        # stop monitoring config file file system changes
        if self.config_file_monitor and self.config_file_monitor.started:
            self.config_file_monitor.stop()

        # unregister from config file data change events
        if self.config_file and self._onConfigDataChange in self.config_file.dataChangeEvent:
            self.config_file.dataChangeEvent -= self._onConfigDataChange

        # stop http server
        if self.http_server:
            self.http_server.stop()
            self.http_server = None

    def update(self):
        return
        self.midi_effect_input.update()

        if self.interval_broadcast:
            self.interval_broadcast.update()

    def applyConfig(self, data):
        #
        # OSC Broadcast/Multicast output
        #
        opts = {'autoStart': True}

        if self.config_file.get_value('py2030.multicast_ip'):
            opts['host'] = self.config_file.get_value('py2030.multicast_ip')
        elif self.config_file.get_value('py2030.broadcast_ip'):
            opts['host'] = self.config_file.get_value('py2030.broadcast_ip')

        if self.config_file.get_value('py2030.multicast_port'):
            opts['port'] = self.config_file.get_value('py2030.multicast_port')

        if not self.broadcast_osc_output:
            self.broadcast_osc_output = Osc(opts)
        else:
            self.broadcast_osc_output.configure(opts)

        #
        # Interval broadcaster
        #
        interval = self.config_file.get_value('py2030.controller.broadcast_interval')
        if (not interval or interval <= 0) and self.interval_broadcast:
            self.interval_broadcast = None
            ColorTerminal().yellow('broadcast interval disabled')

        if interval and interval > 0:
            if self.interval_broadcast:
                self.interval_broadcast.configure({'interval': interval})
                ColorTerminal().yellow('set broadcast interval to {0}'.format(interval))
            else:
                self.interval_broadcast = IntervalBroadcast({'interval': interval, 'data': 'TODO: controller info JSON'})
                ColorTerminal().yellow('started broadcast interval at {0}'.format(interval))

        #
        # http server
        #
        port = self.config_file.get_value('py2030.controller.http_port')
        if port:
            if self.http_server and self.http_server.port != port:
                # stop running http server
                self.http_server.stop()
                self.http_server = None

            # if server not initialized already (or just shutdown)
            if not self.http_server:
                # start http server on (new) port
                self.http_server = HttpServer({'port': port})
                self.http_server.start()
        elif not port and self.http_server:
            self.http_server.stop()

        #
        # midi input
        #
        port = self.config_file.get_value('py2030.controller.midi_in_port')
        if port:
            if self.midi_effect_input.port != port:
                self.midi_effect_input.destroy()
                self.midi_effect_input.port = port
                # start receiving incoming midi message and map them to effect events
                self.midi_effect_input.setup()
        else:
            self.midi_effect_input.destroy()
