from py2030.interface import Interface

class IntervalBroadcast:
    def __init__(self, options = {}):
        # attributes
        self.interface = Interface.instance() # use global interface singleton instance

        # configuration
        self.options = {}
        self.configure(options)

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)
        # TODO; any internal updates needed for the (re-)configuration happen here

    def update(self):
        pass

    # option readers
    def _data(self):
        return self.options['data'] if 'data' in self.options else None

    def _interval(self):
        return self.options['interval'] if 'interval' in self.options else 5.0
