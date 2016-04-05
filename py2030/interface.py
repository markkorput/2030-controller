from py2030.utils.color_terminal import ColorTerminal
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
        self.masters = []

        # special collections
        # for all local changes to resource collections a new models is created in changes
        self.changes = Collections.Changes()
        # all models to the updates collection will automatically be processed and cause
        # the appropriate changes to the local resource collections
        self.updates = Collections.Updates()

        # resource collections are all collection for which all changes (create/update/delete)
        # are propagated into the self.changes collection
        self.addResourceCollection(Collections.Broadcasts, 'broadcasts')

        # events
        self.newModelEvent = Event()

        # configuration
        self.options = {}
        self.configure(options)

        # callbacks
        self.updates.newModelEvent += self._onNewUpdateModel

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)
        # TODO; any internal updates needed for the (re-)configuration happen here

    def add_master(self, interface):
        # start monitoring for any changes on the specified interface
        interface.changes.newModelEvent += self._onNewMasterChangeModel
        # keep list of interfaces we're syncing from
        self.masters.append(interface)

    def _onNewMasterChangeModel(self, model, col):
        # a change in one of our sync source causes and update
        self.updates.create(model.data)

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

    def _onNewUpdateModel(self, model, col):
        try:
            col = getattr(self, model.get('type'))
        except AttributeError as err:
            ColorTerminal().fail('[Interface] got update model with unknown type: ', model.get('type'))
            return

        if model.get('method') == 'create':
            col.create(model.get('data'))
