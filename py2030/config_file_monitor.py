from py2030.utils.color_terminal import ColorTerminal

import os
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler

# Handler class for file system event
class EventHandler(FileSystemEventHandler):
    def __init__(self, config_file):
        self.config_file = config_file

    def on_modified(self, event):
        if event.src_path == self.config_file.path():
            ColorTerminal().output('Config file modified ({0}), reloading content'.format(event.src_path))
            self.config_file.load({'force': True})

class ConfigFileMonitor(FileSystemEventHandler):
    def __init__(self, config_file, start=True):
        self.config_file = config_file
        self.started = False

        if start:
            self.start()

    def __del__(self):
        self.stop()

    def on_modified(self, event):
        if event.src_path == self.config_file.path():
            ColorTerminal().output('Config file modified ({0}), reloading content'.format(event.src_path))
            self.config_file.load({'force': True})

    def start(self):
        if self.started:
            return

        self.observer = Observer()
        self.observer.schedule(self, os.path.dirname(self.config_file.path()))
        self.observer.start()
        self.started = True
        ColorTerminal().success('ConfigFileMonitor started for {0}'.format(self.config_file.path()))

    def stop(self):
        self.observer.stop()
        self.observer.join()
        self.observer = None
        self.started = False
        ColorTerminal().success('ConfigFileMonitor stopped for {0}'.format(self.path()))
