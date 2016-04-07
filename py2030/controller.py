from py2030.utils.color_terminal import ColorTerminal
from py2030.interface import Interface
from py2030.interval_broadcast import IntervalBroadcast
from py2030.outputs.osc import Osc
from py2030.config_file import ConfigFile

class Controller:
    def __init__(self, options = {}):
        # attributes
        self.interface = Interface.instance() # use global interface singleton instance
        self.interval_broadcast = None
        self.broadcast_osc_output = None
        self.config_file = ConfigFile.instance()

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
        # TODO; any internal updates needed for the (re-)configuration happen here

    def setup(self):
        self.config_file.load()
        # apply config
        self.applyConfig(self.config_file.data)
        # start monitoring for file changes
        self.config_file.dataChangeEvent += self._onConfigDataChange
        self.config_file.start_monitoring()

    def _onConfigDataChange(self, data, config_file):
        ColorTerminal().yellow('config change: {0}'.format(data))
        self.applyConfig(data)

    def destroy(self):
        if self.broadcast_osc_output:
            self.broadcast_osc_output.stop()
            self.broadcast_osc_output = None

        if self.config_file:
            self.config_file.stop_monitoring()
            self.config_file = None

    def update(self):
        if self.interval_broadcast:
            self.interval_broadcast.update()

    def applyConfig(self, data):
        # osc broadcaster
        opts = {'autoStart': True}
        host = self.config_file.get_value('py2030.multicast_ip')
        if host:
            opts['host'] = host
        port = self.config_file.get_value('py2030.multicast_port')
        if port:
            opts['port'] = port

        if not self.broadcast_osc_output:
            self.broadcast_osc_output = Osc(opts)
        else:
            self.broadcast_osc_output.configure(opts)

        # interval broadcast
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
