from py2030.interface import Interface
from py2030.inputs.osc import Osc
from py2030.config_file import ConfigFile

class Client:
    def __init__(self, options = {}):
        # attributes
        self.config_file = ConfigFile.instance()
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

    def setup(self):
        self.config_file.load()

        # osc inputs
        opts = {'autoStart': True}

        if self.config_file.get_value('py2030.multicast_ip'):
            opts['multicast'] = self.config_file.get_value('py2030.multicast_ip')
        elif self.config_file.get_value('py2030.broadcast_ip'):
            opts['host'] = self.config_file.get_value('py2030.broadcast_ip')
        if self.config_file.get_value('py2030.multicast_port'):
            opts['port'] = self.config_file.get_value('py2030.multicast_port')

        self.broadcast_osc_input = Osc(opts)

    def update(self):
        self.broadcast_osc_input.update()
