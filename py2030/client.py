from py2030.interface import Interface
from py2030.inputs.osc import Osc
from py2030.config_file import ConfigFile

import urllib2

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

        self.interface.genericEvent += self._onGenericEvent

    def update(self):
        self.broadcast_osc_input.update()

    def _onGenericEvent(self, data):
        typ = data['type'] if 'type' in data else None

        if typ == 'reconfig':
            # print '[Client] /event type reconfig'
            self.config_file.backup()
            try:
                if 'url' in data and data['url']:
                    response = urllib2.urlopen(data['url'])
                else:
                    response = urllib2.urlopen('http://127.0.0.1:2031/config.yaml')

            except urllib2.URLError as err:
                print 'Failed to download config.yaml for reconfig:', err
                response = None

            if response:
                content = response.read()
                print 'downloaded config.yaml: ', content

            # download file
            # self.config_file.write(content_of_downloaded_file)
            # remove downloaded file
