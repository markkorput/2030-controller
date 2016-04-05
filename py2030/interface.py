from py2030.collections.broadcasts import Broadcasts
from py2030.utils.event import Event

class Interface:
    _instance = None

    @classmethod
    def instance(cls, options = {}):
        # Find existing instance
        if Interface._instance:
            return Interface._instance

        # Create instance and save it in the _instance class-attribute
        Interface._instance = Interface(options)
        return Interface._instance

    def __init__(self, options = {}):
        # attributes
        self.broadcasts = Broadcasts()
        self.broadcasts.newModelEvent += self.onNewModel

        # events
        self.newModelEvent = Event()

        # configuration
        self.options = {}
        self.configure(options)

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)
        # TODO; any internal updates needed for the (re-)configuration happen here

    def onNewModel(self, model, collection):
        # simply forward the event to our own listeners, but add self as extra param
        self.newModelEvent(model, collection, self)
