from py2030.interface import Interface
from py2030.utils.configs_file import ConfigsFile

class ConfigRecorder:
    def __init__(self, options = {}):
        # attributes
        self.interface = Interface.instance()
        self.running = False
        self.prefix = '/cfg'

        self.options = {}
        self.configure(options)

    def __del__(self):
        # print 'ConfigRecorder.__del__'
        if self.running:
            self.stop()

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)

        if 'interface' in options:
            wasRunning = self.running
            # stop if running
            if wasRunning: self.stop()
            # change interface
            self.interface = options['interface']
            # restart?
            if wasRunning: self.start()

        if 'path' in options:
            self.file = ConfigsFile(options)

        if 'prefix' in options:
            self.prefix = options['prefix']

    def start(self):
        self.file.load()
        self.interface.oscMessageEvent += self._onOscMessage
        self.running = True

    def stop(self):
        # print 'ConfigRecorder.stop'
        self.file.save()
        self.interface.oscMessageEvent -= self._onOscMessage
        self.running = False

    def _onOscMessage(self, addr, tags, data, client_addr = None):
        if not addr.startswith(self.prefix+'/'):
            return

        sub = addr[len(self.prefix)+1:]
        parts = sub.split('/')

        if len(data) == 2 and addr.endswith('pos'):
            self.file.update_param(parts[0], parts[1]+'_x', data[0])
            self.file.update_param(parts[0], parts[1]+'_y', data[1])
            return

        self.file.update_param(parts[0], parts[1], data[0])
