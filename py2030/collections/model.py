from py2030.utils.event import Event

class Model:
    def __init__(self, data = {}):
        # attributes
        self.data = {}
        self.previous_data = None
        # perform quiet set
        self.reset(data, False)
        # events
        self.updateEvent = Event()

    def reset(self, data = {}, notify = True):
        # remember previous state
        self.previous_data = self.data
        # reset data
        self.data = data
        # send notifications
        if notify:
            self.updateEvent(self, data)

    def update(self, data = {}, notify = True):
        # remember previous state
        self.previous_data = self.data
        # update data
        self.data.update(data)
        # send notifications
        if notify:
            self.updateEvent(self, data)

    def get(self, attr_name):
        if attr_name in self.data:
            return self.data[attr_name]
        return None
