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

    #     # configuration
    #     self.options = {}
    #     self.configure(options)
    #
    # def configure(self, options):
    #     previous_options = self.options
    #     self.options.update(options)
    #     # TODO; any internal updates needed for the (re-)configuration happen here
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

    def clear(self):
        self.models = []
        self.clearEvent(self)

    def __len__(self):
        return len(self.models)

    def __getitem__(self, idx):
        return self.models[idx]
