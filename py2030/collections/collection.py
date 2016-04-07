from py2030.utils.event import Event
from py2030.collections.model import Model

class Collection:
    model = Model

    def __init__(self, options = {}):
        # attributes
        self.model = None
        self.models = []

        # events
        self.newModelEvent = Event()
        self.clearEvent = Event()

    def getModelClass(self):
        return self.model if self.model else self.__class__.model

    def create(self, data = {}):
        model = self.getModelClass()
        new_model = model(data)
        self.add(new_model)
        return new_model

    def add(self, new_model):
        self.models.append(new_model)
        self.newModelEvent(new_model, self)
        return self

    def clear(self):
        self.models = []
        self.clearEvent(self)

    def __len__(self):
        return len(self.models)

    def __getitem__(self, idx):
        return self.models[idx]
