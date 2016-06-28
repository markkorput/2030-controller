from py2030.interface import Interface
from py2030.utils.osc_ascii_file import OscAsciiFile
from py2030.utils.event import Event
from datetime import datetime

class OscAsciiInput:
    def __init__(self, options = {}):
        # attributes
        self.running = False
        self.sync = True # do we care about the osc message timestamps or are we gonna rush through them?
        self.file = OscAsciiFile()
        self.interface = Interface.instance()
        self.verbose = False

        # events
        self.endEvent = Event()

        # config
        self.options = {}
        self.configure(options)

    def __del__(self):
        if self.running:
            self.stop()

    def update(self):
        if not self.running:
            return

        # we're not waiting for loaded frame to go?
        if not self.waitingForSync:
            # read next line
            if not self.file.next_line():
                # reached end of file and we're not looping
                if self.verbose:
                    print '[OscAsciiInput] done'
                self.stop()
                self.endEvent(self)
                return

        # frame-syncing enabled?
        if self.sync:
            t = (datetime.now()-self.start_time).total_seconds()

            # OscAsciiFile keeps timestamp of last read line
            if t < self.file.last_timestamp:
                # wait until it's time for this line
                self.waitingForSync = True
                # keep waiting
                return

            # time to continue
            self.waitingForSync = False

        # pass the new data to the interface
        self.interface.oscMessageEvent(self.file.last_addr, self.file.last_tags, self.file.last_data, None)
        self.message_count += 1
        if self.verbose:
            print '[OscAsciiInput] message count:', self.message_count

    def start(self):
        if self.running:
            self.stop()
        self.file.loopEvent += self._onLoop
        # self.frameSyncTimeShift = 0.0
        self.waitingForSync = False
        self.file.start_reading()
        self.start_time = datetime.now()
        self.message_count = 0
        self.running = True
        # self.startEvent(self)

    def stop(self):
        self.file.stop_reading()
        self.file.loopEvent -= self._onLoop
        self.running = False
        # self.stopEvent(self)

    def configure(self, options):
        # previous_options = self.options
        self.options.update(options)

        if 'loop' in options:
            self.file.set_loop(options['loop'])

        if 'path' in options:
            self.file.set_path(options['path'])

        if 'sync' in options:
            self.sync = options['sync']

        if 'interface' in options:
            self.interface = options['interface']

        if 'verbose' in options:
            self.verbose = options['verbose']

    # the file reader reached the end of the file,
    # and reset back to the start of the file
    def _onLoop(self, natnetFile):
        self.start_time = datetime.now()
        if self.verbose:
            print '[OscAscii-input] loop'
