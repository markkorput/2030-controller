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
        self.registerCallback(False)

    def registerCallback(self, register=True):
        if register:
            # print '[ConfigBroadcaster] registered'
            self.config_file.dataChangeEvent += self._onConfigDataChange
        else:
            # print '[ConfigBroadcaster] unregistered'
            self.config_file.dataChangeEvent -= self._onConfigDataChange

    def _onConfigDataChange(self, data, config_file):
        # print '[ConfigBroadcaster] _onConfigDataChange:', data
        self.interface.genericEvent({'type': 'reconfig'})
