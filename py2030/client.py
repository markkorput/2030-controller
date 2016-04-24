from py2030.interface import Interface
from py2030.inputs.osc import Osc
from py2030.config_file import ConfigFile
from py2030.client_side.reconfig_downloader import ReconfigDownloader
from py2030.utils.color_terminal import ColorTerminal

class Client:
    def __init__(self, options = {}):
        # attributes
        self.config_file = ConfigFile.instance()
        self.client_cache_file = ConfigFile({'path': 'config/client.cache.yaml'})
        self.interface = Interface.instance() # use global interface singleton instance
        self.broadcast_osc_input = None
        self.reconfig_downloader = ReconfigDownloader()

        # configuration
        self.options = {}
        self.configure(options)

        # autoStart is True by default
        if not 'autoStart' in options or options['autoStart']:
            self.setup()

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)

    def _get_client_id_from_config(self):
        config_clients = self.config_file.get_value('py2030.clients')
        if not config_clients:
            return None

        import socket
        myip = socket.gethostbyname(socket.gethostname())
        del socket

        try:
            for client_id in config_clients:
                if 'ip' in config_clients[client_id]:
                    if config_clients[client_id]['ip'] == myip:
                        return client_id
        except:
            ColorTerminal().fail("[Client] error while deriving client id from config.yaml content")

        return None

    def setup(self):
        self.config_file.load()
        self.client_cache_file.load()

        # try to get client id fmor client cache file
        self.client_id = self.client_cache_file.get_value('py2030.client_id')

        # if we couldn't get client id form client cache file; get it from config file and save it to client cache file
        if not self.client_id:
            ColorTerminal().warn("Could not get client_id form client.cache.yaml, trying config file.")
            self.client_id = self._get_client_id_from_config()
            if self.client_id:
                # create client cache file / update client cache file with client id
                client_cache_data = self.client_cache_file.data if self.client_cache_file.data else {}
                if not 'py2030' in client_cache_data:
                    client_cache_data['py2030'] = {}
                client_cache_data['py2030']['client_id'] = self.client_id
                # write data to cache file
                ColorTerminal().output("Writing client_id to client.cache.yaml")
                self.client_cache_file.write_yaml(client_cache_data)
            else:
                ColorTerminal().warn("Couldn't get client_id, assuming 1")
                self.client_id = 1

        # osc inputs
        opts = {'autoStart': True}

        if self.config_file.get_value('py2030.multicast_ip'):
            opts['multicast'] = self.config_file.get_value('py2030.multicast_ip')
        elif self.config_file.get_value('py2030.broadcast_ip'):
            opts['host'] = self.config_file.get_value('py2030.broadcast_ip')
        if self.config_file.get_value('py2030.multicast_port'):
            opts['port'] = self.config_file.get_value('py2030.multicast_port')

        self.broadcast_osc_input = Osc(opts)

        self.reconfig_downloader.setup()


    def update(self):
        self.broadcast_osc_input.update()
