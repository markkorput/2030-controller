from py2030.utils.event import Event
import os

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler

class EventHandler(FileSystemEventHandler):
    def __init__(self, config_file):
        self.config_file = config_file
        self.path = self.config_file.path()

    def on_modified(self, event):
        if event.src_path == self.path:
            self.config_file.fileChangeEvent(self.config_file)


class ConfigFile:
    def __init__(self, options = {}):
        # attributes
        self.monitoring = False

        # events
        self.fileChangeEvent = Event()

        # config
        self.options = {}
        self.configure(options)

    def __del__(self):
        if self.monitoring:
            self.stop_monitoring()

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)
        
        if 'path' in options and self.monitoring:
            self.stop_monitoring()
            self.start_monitoring()

    def path(self):
        return self.options['path'] if 'path' in self.options else None

    def folder_path(self):
        return os.path.dirname(self.path())

    def read(self):
        f = open(self.path(), 'r')
        content = f.read()
        f.close()
        return content

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

    def stop_monitoring(self):
        self.observer.stop()
        self.observer.join()
        self.observer = None
        self.monitoring = False

