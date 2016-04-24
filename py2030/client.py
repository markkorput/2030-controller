from py2030.interface import Interface
from py2030.inputs.osc import Osc
from py2030.config_file import ConfigFile
from py2030.client_side.reconfig_downloader import ReconfigDownloader
from py2030.client_side.client_info import ClientInfo

class Client:
    def __init__(self, options = {}):
        # attributes
        self.config_file = ConfigFile.instance()
        self.interface = Interface.instance() # use global interface singleton instance
        self.broadcast_osc_input = None
        self.reconfig_downloader = ReconfigDownloader()
        self.client_info = ClientInfo()

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

        print 'client-id: ', self.client_info.client_id()

        #
        # osc input
        #
        opts = {'autoStart': True}

        if self.config_file.get_value('py2030.multicast_ip'):
            opts['multicast'] = self.config_file.get_value('py2030.multicast_ip')
        elif self.config_file.get_value('py2030.broadcast_ip'):
            opts['host'] = self.config_file.get_value('py2030.broadcast_ip')
        if self.config_file.get_value('py2030.multicast_port'):
            opts['port'] = self.config_file.get_value('py2030.multicast_port')

        self.broadcast_osc_input = Osc(opts)

        #
        # ReconfigDownloader
        #
        self.reconfig_downloader.setup()

    def update(self):
        self.broadcast_osc_input.update()
