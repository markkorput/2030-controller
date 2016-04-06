from py2030.utils.color_terminal import ColorTerminal
from py2030.interface import Interface
from py2030.interval_broadcast import IntervalBroadcast
from py2030.outputs.osc import Osc
from py2030.config_file import ConfigFile

class Controller:

    config_file_paths = ('config/config.json', '../config/config.json')

    def __init__(self, options = {}):
        # attributes
        self.interface = Interface.instance() # use global interface singleton instance
        self.interval_broadcast = IntervalBroadcast({'interval': 5.0, 'data': 'TODO: controller info JSON'})
        self.osc_output = None

        # configuration
        self.options = {}
        self.configure(options)

        # autoStart is True by default
        if not 'autoStart' in options or options['autoStart']:
            self.setup()

    def __del__(self):
        self.destroy()

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)
        # TODO; any internal updates needed for the (re-)configuration happen here

    def setup(self):
        for config_path in self.__class__.config_file_paths:
            self.config_file = ConfigFile({'path': config_path})
            if self.config_file.exists():
                # changes to the config file will be directly ingested
                self.config_file.dataChangeEvent += self._onConfigDataChange
                self.config_file.start_monitoring()
                break

        if not self.config_file.exists():
            ColorTerminal().fail('[Controller] could not find config file, using defaults')

        self.osc_output = Osc() # auto connects

    def destroy(self):
        if self.osc_output:
            self.osc_output.stop()
            self.osc_output = None

    def update(self):
        self.interval_broadcast.update()

    def _onConfigDataChange(self, data, config_file):
        ColorTerminal().yellow('config change: {0}'.format(data))
