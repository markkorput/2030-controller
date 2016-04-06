from py2030.utils.event import Event
from py2030.utils.color_terminal import ColorTerminal

import os, json, yaml
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler

# Handler class for file system event
class EventHandler(FileSystemEventHandler):
    def __init__(self, config_file):
        self.config_file = config_file

    def on_modified(self, event):
        self.config_file.reload()

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
        self.monitoring = False
        self.previous_data = None
        self.data = None

        # events
        self.dataChangeEvent = Event()

        # config
        self.options = {}
        self.configure(options)

        if 'monitor' in self.options and self.options['monitor']:
            self.start_monitoring()

    def __del__(self):
        if hasattr(self, 'monitoring') and self.monitoring:
            self.stop_monitoring()

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)

        if 'path' in options:
            if self.monitoring:
                self.stop_monitoring()
                self.start_monitoring()

    def reload(self):
        new_data = None
        try:
            if self.path().endswith('.yaml'):
                new_data = yaml.load(self.read())
            elif self.path().endswith('.json'):
                new_data = json.loads(self.read())
            else:
                ColorTerminal().fail('[ConfigFile] could not determine config file data format from file name: '+self.path())
        except ValueError as err:
            ColorTerminal().fail("Couldn't parse config file: {0}".format(self.path()))
            return

        if new_data:
            self.previous_data = self.data
            self.data = new_data
            self.dataChangeEvent(new_data, self)

    def path(self):
        return self.options['path'] if 'path' in self.options else None

    def folder_path(self):
        return os.path.dirname(self.path())

    def read(self):
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

    def start_monitoring(self):
        if self.monitoring:
            return

        self.event_handler = EventHandler(config_file=self)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.folder_path())
        self.observer.start()
        self.monitoring = True
        ColorTerminal().success('ConfigFile started monitoring {0}'.format(self.path()))

    def stop_monitoring(self):
        self.observer.stop()
        self.observer.join()
        self.observer = None
        self.monitoring = False
        ColorTerminal().success('ConfigFile stopped monitoring {0}'.format(self.path()))

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
