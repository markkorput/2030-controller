from py2030.interface import Interface
from py2030.config_file import ConfigFile

class ConfigBroadcaster:
    def __init__(self, options={}):
        # params
        self.options = options

        # attributes
        self.interface = options['interface'] if 'interface' in options else Interface.instance()
        self.config_file = options['config_file'] if 'config_file' in options else ConfigFile.instance()

        # setup
        self.registerCallback()

    def __del__(self):
        # tear down
        self.destroy()

    def destroy(self):
        self.registerCallback(False)

    def registerCallback(self, register=True):
        if register:
            print '[ConfigBroadcaster] registered'
            self.config_file.dataChangeEvent += self._onConfigDataChange
        else:
            if self._onConfigDataChange in self.config_file.dataChangeEvent:
                print '[ConfigBroadcaster] unregistered'
                self.config_file.dataChangeEvent -= self._onConfigDataChange

    def url(self):
        if hasattr(self, '__url'):
            return self.__url

        self.config_file.load()
        http_port = self.config_file.get_value('py2030.controller.http_port')

        if not http_port:
            return None

        import socket
        self.__hostname = socket.gethostbyname(socket.gethostname())
        del socket

        self.__url = "http://{0}:{1}/{2}".format(self.__hostname, http_port, self.config_file.path())
        return self.__url

    def _onConfigDataChange(self, data, config_file):
        # print '[ConfigBroadcaster] _onConfigDataChange:', data
        self.interface.genericEvent({'type': 'reconfig', 'url': self.url()})
