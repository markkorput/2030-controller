from py2030.interface import Interface

from datetime import datetime

class IntervalBroadcast:
    def __init__(self, options = {}):
        # attributes
        self.interface = Interface.instance() # use global interface singleton instance

        # configuration
        self.options = {}
        self.configure(options)

        # schedule first broadcast; immediately
        self.startTime = datetime.now()
        self.nextBroadcastTime = 0.0 # self.interval()
        self.time = 0.0

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)

    def update(self, dt=None):
        if dt:
            self.time = self.time + dt
        else:
            self.time = (datetime.now() - self.startTime).total_seconds()

        # using while to catch-up with any missed broadcasts (mainly for testing-purposes)
        if self.time >= self.nextBroadcastTime:
            # broadcast
            self.broadcast()
            # schedule next broadcast
            self.nextBroadcastTime = self.time + self.interval()

    def broadcast(self):
        # self.interface.broadcasts.create(self.data())
        self.interface.genericEvent({'type': 'broadcast', 'data': self.data()})

    # option readers
    def data(self):
        return self.options['data'] if 'data' in self.options else None

    def interval(self):
        return self.options['interval'] if 'interval' in self.options else 5.0
