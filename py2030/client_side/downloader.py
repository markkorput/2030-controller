from py2030.utils.color_terminal import ColorTerminal
from py2030.interface import Interface
from py2030.config_file import ConfigFile
from py2030.utils.event import Event

import os

class Downloader:
    def __init__(self, options = {}):
        # params
        self.options = options

        # attributes
        self.config_file = self.options['config_file'] if 'config_file' in self.options else ConfigFile.instance()
        self.interface = self.options['interface'] if 'interface' in self.options else Interface.instance()

        # event(s)
        self.configUpdateEvent = Event()
        self.newVersionEvent = Event()

    def __del__(self):
        self.destroy()

    def configure(self, opts):
        self.options.update(opts)

    def setup(self):
        if not self._onGenericEvent in self.interface.genericEvent:
            print 'ReconfigDownloader registered'
            self.interface.genericEvent += self._onGenericEvent

        if not self._onAck in self.interface.ackEvent:
            self.interface.ackEvent += self._onAck

    def destroy(self):
        if self._onGenericEvent in self.interface.genericEvent:
            print 'ReconfigDownloader de-registered'
            self.interface.genericEvent -= self._onGenericEvent

    def _onGenericEvent(self, data):
        typ = data['type'] if 'type' in data else None

        if typ != 'reconfig':
            return

        # print '[ReconfigDownloader] reconfig event:', data
        url = data['url'] if 'url' in data and data['url'] else 'http://127.0.0.1:2031/config.yaml'

        import urllib2

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

    def _onAck(self, data):
        my_version = self.config_file.get_value('py2030.version')
        if not 'version' in data or data['version'] == my_version:
            return

        ColorTerminal().warn('ack response gave different version: ' + data['version'])
        print data
        if not 'version_download_url' in data:
            ColorTerminal().warn("didn't get version-download-url, staying on current version: " + my_version)
            return

        import urllib

        target_path = 'data/py2030-'+data['version']+'.tar.gz'
        if os.path.isfile(target_path):
            print 'other version already available'
        else:
            # blocking
            # subprocess.call(['wget', data['version_download_url'])

            print 'Downloading app version: ', data['version_download_url']
            urllib.urlretrieve(data['version_download_url'], target_path)

            if os.path.isfile(target_path):
                print 'Download complete'
            else:
                print 'Download failed, continuing on current version'
                return

        self._applyVersionFile(target_path)

        print('Downloader applying version to config file')
        content = self.config_file.read() # make sure it's loaded with current content
        content = content.replace("version: '"+my_version+"'", "version: '"+data['version']+"'")
        self.config_file.write(content)

        print 'Downloader triggering newVersionEvent'
        self.newVersionEvent(data['version'], self)
        self.interface.restartEvent()

    def _applyVersionFile(self, path):
        command = 'tar -zxf '+path+' -C data'
        print '[Downloader] extracting new version with', command
        os.system(command)

        command = 'mv py2030 py2030.bak'
        print '[Downloader] backing up existing module with', command
        os.system(command)

        command = 'mv data/py2030 ./'
        print '[Downloader] moving downloaded module into position with', command
        os.system(command)
