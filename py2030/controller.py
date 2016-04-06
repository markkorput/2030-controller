from py2030.utils.color_terminal import ColorTerminal
from py2030.interface import Interface
from py2030.interval_broadcast import IntervalBroadcast
from py2030.outputs.osc import Osc
from py2030.config_file import ConfigFile

class Controller:
    def __init__(self, options = {}):
        # attributes
        self.interface = Interface.instance() # use global interface singleton instance
        self.interval_broadcast = IntervalBroadcast({'interval': 5.0, 'data': 'TODO: controller info JSON'})
        self.broadcast_osc_output = None
        self.config_file = None

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
        # config file; load global instance
        self.config_file = ConfigFile.instance()
        # start monitoring for file changes
        self.config_file.start_monitoring()
        # if config file exists, loads its content
        if self.config_file.exists():
            self.config_file.reload()
        else:
            ColorTerminal().fail('[Controller] could not find config file, using defaults')

        # osc broadcaster
        opts = {'autoStart': True}

        if 'py2030' in self.config_file.data:
            if 'multicast_ip' in self.config_file.data['py2030']:
                opts['host'] = self.config_file.data['py2030']['multicast_ip']
            if 'multicast_port' in self.config_file.data['py2030']:
                opts['port'] = self.config_file.data['py2030']['multicast_port']

        self.broadcast_osc_output = Osc(opts) # auto connects

    def destroy(self):
        if self.broadcast_osc_output:
            self.broadcast_osc_output.stop()
            self.broadcast_osc_output = None

        if self.config_file:
            self.config_file.stop_monitoring()
            self.config_file = None

    def update(self):
        self.interval_broadcast.update()

    def _onConfigDataChange(self, data, config_file):
        ColorTerminal().yellow('config change: {0}'.format(data))
