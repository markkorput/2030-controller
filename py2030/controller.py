
class Controller:
    def __init__(self, options = {}):
        self.options = {}
        self.configure(options)

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)
        # TODO; any internal updates needed for the (re-)configuration happen here

    def update(self):
        pass
