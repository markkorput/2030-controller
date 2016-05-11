from py2030.interface import Interface

class Syncer:
    def __init__(self, opts = {}):
        self.options = opts

        # default to singleton Interface instance
        self.interface = self.options['interface'] if 'interface' in self.options else Interface.instance()

        # attributes
        self._pending_pings = []

    def __del__(self):
        self.destroy()

    def setup(self):
        print "syncer setup"
        self.interface.pingEvent += self._onPing
        self.interface.pongEvent += self._onPong

    def destroy(self):
        if self.interface.pingEvent.handles(self._onPing):
            self.interface.pingEvent -= self._onPing
        if self.interface.pongEvent.handles(self._onPong):
            self.interface.pongEvent -= self._onPong

    def update(self):
        pass


    def ping_data(self, client_id):
        return {
            'client_id': client_id,
            'app_time': 0.0, # TODO
            'player_time': 0.0, # TODO
            'known_delay': 0.0 # TODO
        }

    def ping(self, client_id):
        # trigger pingEvent on interface, the appropriate OSC output should pick it up
        # and distribute the message
        self.interface.pingEvent(self.ping_data(client_id))

    def _onPing(self, data):
        # TODO;
        pass

    def _onPong(self, data):
        pass
