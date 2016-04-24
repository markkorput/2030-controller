from py2030.utils.event import Event
from py2030.utils.color_terminal import ColorTerminal

import os, json, yaml

class ConfigFile:
    default_paths = ('config/config.yaml', '../config/config.yaml', 'config/config.yaml.default', '../config/config.yaml.default')

    _instance = None

    @classmethod
    def instance(cls, options = {}):
        # Find existing instance
        if cls._instance:
            return cls._instance

        # unless path is specified, we'll try to find an
        # existing config file at the expected paths
        if not 'path' in options:
            for path in cls.default_paths:
                if os.path.isfile(path):
                    options['path'] = path
                    break

        # Create instance and save it in the _instance class-attribute
        cls._instance = cls(options)
        return cls._instance

    def __init__(self, options = {}):
        # attributes
        self.previous_data = None
        self.data = None

        # events
        self.dataLoadedEvent = Event()
        self.dataChangeEvent = Event()

        # config
        self.options = {}
        self.configure(options)

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)

    def load(self, options = {}):
        # already have data loaded?
        if self.data != None:
            # we'll need the {'force': True} option to force a reload
            if not 'force' in options or options['force'] != True:
                # abort
                return

        content = self.read()
        if not content:
            return

        if self.path().endswith('.yaml'):
            self.loadYaml(content)
        elif self.path().endswith('.json'):
            self.loadJson(content)
        else:
            ColorTerminal().warn('[ConfigFile] could not determine config file data format from file name ({0}), assuming yaml'.format(self.path()))
            self.loadYaml(content)

    def loadJson(self, content):
        try:
            new_data = json.loads(content)
        except:
            ColorTerminal().warn("[ConfigFile] json corrupted ({0}), can't load data".format(self.path()))
            return
        self.setData(new_data)

    def loadYaml(self, content):
        try:
            new_data = yaml.load(content)
        except:
            ColorTerminal().warn("[ConfigFile] yaml corrupted ({0}), can't load data".format(self.path()))
            return
        self.setData(new_data)

    def setData(self, new_data):
        self.previous_data = self.data
        self.data = new_data
        if self.previous_data != new_data:
            if self.previous_data == None:
                self.dataLoadedEvent(new_data, self)
            else:
                self.dataChangeEvent(new_data, self)

    def path(self):
        return self.options['path'] if 'path' in self.options else None

    def read(self):
        if not self.exists():
            ColorTerminal().warn("[ConfigFile] file doesn't exist, can't read content ({0})".format(self.path()))
            return None
        f = open(self.path(), 'r')
        content = f.read()
        f.close()
        return content

    def write_yaml(self, yaml):
        self.write(yaml.dump(yaml))

    def write(self, content):
        f = open(self.path(), 'w')
        f.write(content)
        f.close()

    def exists(self):
        return os.path.isfile(self.path())

    def get_value(self, path):
        data = self.data if self.data else {}
        names = path.split('.')
        for name in names:
            if not name in data:
                return None
            data = data[name]
        return data
