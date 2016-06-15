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

        # resource collections are all collection for which
        # all changes (create/update/delete) are propagated
        # into the self.changes collection
        self.add_resource_collection(Collections.Broadcasts, 'broadcasts')

        # events
        self.newModelEvent = Event()

        # network distributed events
        self.genericEvent = Event() # for prototyping
        self.effectEvent = Event() # for triggering realtime visual effects
        # joinEvent;
        # clients; triggered to ask to join the network
        # controller; triggered when a join request comes in
        self.joinEvent = Event()
        # triggered on client side when an ack message is received in response to join request
        self.ackEvent = Event()
        # triggered on both controller and clients when ableton
        # stars a new clip (controller will forward this event over the network)
        self.clipEvent = Event()
        # ping/pong for syncing
        self.pingEvent = Event() # triggered to ping/when being pinged
        self.pongEvent = Event() # triggered to pong/when being ponged
        self.restartEvent = Event() # triggered when receiving as restart command
        # triggered when an Osc message came in that simply has to be forwarded to all connected clients
        self.oscMessageEvent = Event()

        self.ledValueEvent = Event()

        # configuration
        self.options = {}
        self.configure(options)

        # callbacks
        self.updates.newModelEvent += self._onNewUpdateModel

    def __del__(self):
        self.destroy()

    def destroy(self):
        for master in self.masters:
            master.changes.newModelEvent -= self._onNewMasterChangeModel
        self.masters = []

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)

    # start monitoring the given interface's changes collection
    # and forwarding new models into our own updates collection
    # effectively copying and new resource collection model
    def add_master(self, interface):
        # start monitoring for any changes on the specified interface
        interface.changes.newModelEvent += self._onNewMasterChangeModel
        # keep list of interfaces we're syncing from
        self.masters.append(interface)

    def _onNewMasterChangeModel(self, model, col):
        # a change in one of our sync source causes and update
        self.updates.create(model.data)

    def add_resource_collection(self, cls, type, options = {}):
        # create new instance of the collection
        col = cls()
        # set it as an attribute with type-string as name
        setattr(self, type, col)
        # give the collection a serialize_name attribute, used when recording changes
        cls.serialize_name = options['serialize_name'] if 'serialize_name' in options else type
        # register callback
        col.newModelEvent += self._onNewModel

    def _onNewModel(self, model, collection):
        # Interface 'records' all local changes (create/update/delete) to its collections
        # into the changes collection
        self.changes.create({'method': 'create', 'type': collection.serialize_name, 'data': model.data})

        # we'll forward the event to our own listeners, but add self as extra param
        self.newModelEvent(model, collection, self)

    def _onNewUpdateModel(self, model, col):
        try:
            col = getattr(self, model.get('type'))
        except AttributeError as err:
            ColorTerminal().fail('[Interface] got update model with unknown type: ', model.get('type'))
            return

        if model.get('method') == 'create':
            col.create(model.get('data'))
            return

        ColorTerminal().warn('[Interface] got update model with unknown method: ', model.get('method'))
