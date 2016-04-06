from py2030.interface import Interface
from py2030.inputs.osc import Osc
from py2030.config_file import ConfigFile

class Client:
    def __init__(self, options = {}):
        # attributes
        self.interface = Interface.instance() # use global interface singleton instance
        self.broadcast_osc_input = None

        # configuration
        self.options = {}
        self.configure(options)

        # autoStart is True by default
        if not 'autoStart' in options or options['autoStart']:
            self.setup()

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
            ColorTerminal().fail('[Client] could not find config file, using defaults')

        # osc inputs
        opts = {'autoStart': True}
        if 'py2030' in self.config_file.data:
            if 'multicast_ip' in self.config_file.data['py2030']:
                opts['multicast'] = self.config_file.data['py2030']['multicast_ip']
            if 'multicast_port' in self.config_file.data['py2030']:
                opts['port'] = self.config_file.data['py2030']['multicast_port']

        self.broadcast_osc_input = Osc(opts) # auto connects

    def update(self):
        self.broadcast_osc_input.update()
