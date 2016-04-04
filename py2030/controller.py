from py2030.interface import Interface
from py2030.interval_broadcast import IntervalBroadcast
from py2030.outputs.osc import Osc

class Controller:
    def __init__(self, options = {}):
        # attributes
        self.interface = Interface.instance() # use global interface singleton instance
        self.interval_broadcast = IntervalBroadcast({'interval': 5.0, 'data': 'TODO: controller info JSON'})
        self.isSetup = False

        # configuration
        self.options = {}
        self.configure(options)

        # autoStart is True by default
        if not 'autoStart' in options or options['autoStart']:
            self.setup()

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)
        # TODO; any internal updates needed for the (re-)configuration happen here

    def setup(self):
        self.osc_output = Osc() # auto connects
        self.isSetup = True

    def destroy(self):
        self.osc_output.stop()
        self.isSetup = False

    def update(self):
        self.interval_broadcast.update()