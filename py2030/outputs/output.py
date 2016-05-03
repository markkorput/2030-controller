from py2030.utils.color_terminal import ColorTerminal
from py2030.interface import Interface
from py2030.utils.event import Event

class Output:
    def __init__(self, options = {}):
        # attributes
        self.interface = None

        # defaults
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

        # new interface?
        if 'interface' in options:
            # unregister from current interface
            if self.interface:
                self.interface.changes.newModelEvent -= self._onChange
                self.interface.genericEvent -= self._onGenericEvent
                self.interface.effectEvent -= self._onEffect
                self.interface.joinEvent -= self._onJoin

            # set interface as attribute
            self.interface = options['interface']

            # register on new interface
            if self.interface:
                self.interface.changes.newModelEvent += self._onChange
                self.interface.genericEvent += self._onGenericEvent
                self.interface.effectEvent += self._onEffect
                self.interface.joinEvent += self._onJoin

        if ('accept_types' in options or 'ignore_types' in options) and 'accept_types' in self.options and 'ignore_types' in self.options:
            both = list(set(self.options['accept_types']) & set(self.options['ignore_types']))
            if len(both) > 0:
                ColorTerminal().warn("[Output] these types are specified to be both ignored and accepted, they will be ignored: {0}".format(both))

    def output(self, change_model):
        # overwrite this method with output-specific logic
        pass

    def _onChange(self, change_model, collection):
        if 'accept_types' in self.options and not change_model.get('type') in self.options['accept_types']:
            return

        if 'ignore_types' in self.options and change_model.get('type') in self.options['ignore_types']:
            return

        self.output(change_model)
        self.outputEvent(change_model, self)

    def trigger(self, event, data):
        # overwrite this method with output-specific logic
        pass

    def _onGenericEvent(self, effect_data):
        if self.outputGenericEvent():
            self.trigger('event', effect_data)

    def _onEffect(self, effect_data):
        if self.outputEffect():
            self.trigger('effect', effect_data)

    def _onJoin(self, join_data):
        if self.outputJoin():
            self.trigger('join', join_data)

    def outputGenericEvent(self):
        return not 'outputs' in self.options or self.options['outputs'].count('events') > 0

    def outputEffect(self):
        return not 'outputs' in self.options or self.options['outputs'].count('effects') > 0

    def outputJoin(self):
        return 'outputs' in self.options and self.options['outputs'].count('joins') > 0
