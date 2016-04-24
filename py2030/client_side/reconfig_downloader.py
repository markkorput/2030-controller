from py2030.interface import Interface
from py2030.config_file import ConfigFile
from py2030.utils.event import Event

import urllib2

class ReconfigDownloader:
    def __init__(self, options = {}):
        # params
        self.options = options

        # attributes
        self.config_file = self.options['config_file'] if 'config_file' in self.options else ConfigFile.instance()
        self.interface = self.options['interface'] if 'interface' in self.options else Interface.instance()

        # event(s)
        self.configUpdateEvent = Event()

    def __del__(self):
        self.destroy()

    def setup(self):
        self.interface.genericEvent += self._onGenericEvent

    def destroy(self):
        self.interface.genericEvent -= self._onGenericEvent

    def _onGenericEvent(self, data):
        typ = data['type'] if 'type' in data else None

        if typ != 'reconfig':
            return

        # print '[ReconfigDownloader] reconfig event:', data
        url = data['url'] if 'url' in data and data['url'] else 'http://127.0.0.1:2031/config.yaml'

        try:
            response = urllib2.urlopen(url)
        except urllib2.URLError as err:
            print err, 'Failed to download reconfig file from', url
            return

        # backup current config file to ocnfig.yaml.bak.<timestamp>
        self.config_file.backup()
        # get downloaded content and write it to our config file
        content = response.read()
        self.config_file.write(content)
        # print 'Todo; apply new config settings at runtime'
        self.configUpdateEvent(self)
