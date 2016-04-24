from py2030.config_file import ConfigFile
from py2030.utils.color_terminal import ColorTerminal

class ClientInfo:
    def __init__(self, options = {}):
        # params
        self.options = options
        self._client_id = None

        # attributes
        self.config_file = self.options['config_file'] if 'config_file' in self.options else ConfigFile.instance()
        self.client_cache_file = ConfigFile({'path': 'config/client.cache.yaml'})

    def client_id(self):
        if not self._client_id:
            self._client_id = self._get_client_id()
        return self._client_id

    def _get_client_id(self):
        self.client_cache_file.load()

        # try to get client id fmor client cache file
        client_id = self.client_cache_file.get_value('py2030.client_id')

        # if we couldn't get client id form client cache file; get it from config file and save it to client cache file
        if not client_id:
            ColorTerminal().warn("Could not get client_id form client.cache.yaml, trying config file.")
            client_id = self._get_client_id_from_config()
            if client_id:
                # create client cache file / update client cache file with client id
                client_cache_data = self.client_cache_file.data if self.client_cache_file.data else {}
                if not 'py2030' in client_cache_data:
                    client_cache_data['py2030'] = {}
                client_cache_data['py2030']['client_id'] = client_id
                # write data to cache file
                ColorTerminal().output("Writing client_id to client.cache.yaml")
                self.client_cache_file.write_yaml(client_cache_data)
            else:
                ColorTerminal().warn("Couldn't get client_id, assuming 1")
                client_id = 1

        return client_id

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
