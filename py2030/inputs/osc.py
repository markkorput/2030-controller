from py2030.utils.color_terminal import ColorTerminal
from py2030.interface import Interface

try:
    from OSC import OSCServer
except ImportError:
    ColorTerminal().warn("importing embedded version of pyOSC library for py2030.inputs.osc")
    from py2030.dependencies.OSC import OSCServer

class Osc:
    def __init__(self, options = {}):
        # attributes
        self.interface = Interface.instance() # use global interface singleton instance

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
        pass
