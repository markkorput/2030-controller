from py2030.interface import Interface
from py2030.inputs.osc import Osc

class Client:
    def __init__(self, options = {}):
        # attributes
        self.interface = Interface.instance() # use global interface singleton instance
        self.osc_input = Osc() # uses same global instance of interface be default

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
        pass

    def update(self):
        self.osc_input.update()
