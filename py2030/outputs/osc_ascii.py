from py2030.interface import Interface
from py2030.utils.osc_ascii_file import OscAsciiFile
from py2030.utils.color_terminal import ColorTerminal

from datetime import datetime

class OscAscii:
    def __init__(self, options = {}):
        # attributes
        self.running = False
        self.file = OscAsciiFile()
        self.line_count = 0
        self.verbose = False
        self.start_time = None

        # configuration
        if not 'interface' in options:
            options['interface'] = Interface.instance()

        self.options = {}
        self.configure(options)

    def __del__(self):
        if self.running:
            self.stop()

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)

        # path change?
        if 'path' in options:
            wasRunning = self.running

            if wasRunning: # stop current file recording
                self.stop()

            # new output file (path)
            self.file = OscAsciiFile(path=options['path'])

            if wasRunning: # continue?
                self.start()

        # interface change?
        if 'interface' in options:
            # unregister from previous interface
            if 'interface' in previous_options and previous_options['interface']:
                previous_options['interface'].oscMessageEvent -= self._onOscMessage

            # register with new interface
            if options['interface']:
                options['interface'].oscMessageEvent += self._onOscMessage

        if 'verbose' in options:
            self.verbose = options['verbose']

    def start(self):
        # ColorTerminal().green('OscAscii writing to: ' + str(self.file.path))
        self.file.start_writing()
        if not self.trimTimeBeforeFirstMessage():
            self.start_time = datetime.now()
        self.running = True

    def stop(self):
        self.file.stop_writing()
        self.start_time = None
        self.running = False

    def trimTimeBeforeFirstMessage(self):
        return 'trim' in self.options and self.options['trim']

    def _onOscMessage(self, addr, tags, data, client_addr):
        if self.running:
            if not self.start_time:
                self.start_time = datetime.now()

            t = (datetime.now() - self.start_time).total_seconds()
            self.file.write_line(addr, tags, data, t)
            self.line_count += 1
            if self.verbose:
                print '[OscAscii] recorded lines: ' + str(self.line_count)
