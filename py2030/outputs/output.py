from py2030.interface import Interface
from py2030.utils.event import Event

class Output:
    def __init__(self, options = {}):
        # attributes
        self.interface = None

        # default
        if not 'interface' in options:
            options['interface'] = Interface.instance()

        # events
        self.outputEvent = Event()

        # configure
        self.options = {}
        self.configure(options)

    def configure(self, options):
        self.previous_options = self.options
        self.options.update(options)

        if 'interface' in options:
            if self.interface:
                self.interface.changes.newModelEvent -= self._onNewChange

            self.interface = options['interface']

            if self.interface:
                self.interface.changes.newModelEvent += self._onNewChange

    def output(self, change_model):
        # overwrite this method with output-specific logic
        pass

    def _onNewChange(self, change_model, collection):
        self.output(change_model)
        self.outputEvent(change_model, self)
