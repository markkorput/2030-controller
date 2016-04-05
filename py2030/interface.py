import py2030.collections.collections as Collections
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
        self.changes = Collections.Changes()
        self.addResourceCollection(Collections.Broadcasts, 'broadcasts')

        # events
        self.newModelEvent = Event()

        # configuration
        self.options = {}
        self.configure(options)

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)
        # TODO; any internal updates needed for the (re-)configuration happen here

    def addResourceCollection(self, cls, type):
        # create new instance of the collection
        col = cls()
        # set it as attr on self
        setattr(self, type, col)
        cls.serialize_name = type
        # register callbacks
        col.newModelEvent += self.onNewModel

    def onNewModel(self, model, collection):
        # we'l forward the event to our own listeners, but add self as extra param
        self.newModelEvent(model, collection, self)

        # Interface 'records' all local changes (create/update/delete) to its collections
        # into the changes collection
        self.changes.create({'method': 'create', 'type': collection.serialize_name, 'data': model.data})
