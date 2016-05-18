from py2030.utils.color_terminal import ColorTerminal
from py2030.utils.event import Event

import struct, os
from datetime import datetime

class OscAsciiFile:
    def __init__(self, path=None, loop=True):
        # params
        self.path = path
        self.loop = loop

        # file handles
        self.read_file = None
        self.write_file = None

        # last read frame info
        self.last_line = None
        self.last_timestamp = None
        self.last_addr = None
        self.last_tags = None
        self.last_data = None

        # other attribute(s)
        self._separation_character = ','

        # events
        self.loopEvent = Event()

    def __del__(self):
        self.stop()

    def _default_read_file_path(self):
        # return 'data/ascii_osc_file.csv'
        files = os.listdir('dir')
        files = filter(lambda f: f.startswith('ascii_osc_file_') and f.endswith('.csv'), files).sort()
        return fs[-1] if len(fs) > 0 else 'data/ascii_osc_file.csv'

    def start_reading(self):
        self.stopReading()

        try:
            if not self.path or self.path == 'auto':
                self.path = self._default_read_file_path()

            # self.read_file = open(self.path, 'rb')
            self.read_file = open(self.path, 'r')
            ColorTerminal().success("OscAsciiFile opened: %s" % self.path)
        except:
            ColorTerminal().fail("OscAsciiFile couldn't be opened: %s" % self.path)
            self.read_file = None

    def stop_reading(self):
        if self.read_file:
            self.read_file.close()
            self.read_file = None
            ColorTerminal().blue('OscAsciiFile closed')

    def start_writing(self):
        self.stop_writing()
        try:
            if not self.path or self.path == 'auto':
                self.path = 'data/ascii_osc_file_'+datetime.now().strftime('%Y_%m_%d_%H_%M_%S')+'.csv'

            # self.write_file = open(self.path, 'wb')
            self.write_file = open(self.path, 'w')
            ColorTerminal().success("OscAsciiFile opened for writing: %s" % self.path)
        except:
            ColorTerminal().fail("OscAsciiFile couldn't be opened for writing: %s" % self.path)
            self.write_file = None

    def stop_writing(self):
        if self.write_file:
            self.write_file.close()
            self.write_file = None
            ColorTerminal().blue('OscAsciiFile closed')

    def stop(self):
        self.stop_reading()
        self.stop_writing()

    def set_path(self, path):
        self.path = path

    def set_loop(self, loop):
        self.loop = loop

    def next_line(self):
        # read a line from the file
        line = self.read_file.readline()

        # end-of-file?
        if line == '':
            if not self.loop:
                return False

            # rewind file handle te start of file
            self.read_file.seek(0)
            self.loopEvent(self)
            # try again
            # TODO; do check to avoid endless recursion for empty files?
            return self.next_line()

        self.last_line = line
        # parse line into attributes; first separate the line into csv columns
        columns = line.split(self._separation_character)
        # float timestamp
        self.last_timestamp = float(columns[0])
        # string address
        self.last_addr = columns[1]
        # params (param types and param values)
        idx = 2
        count = len(columns)
        self.last_tags = []
        self.last_data = []

        while idx < (count-1): # need two more columns each iteration
            tag = columns[idx]
            value = columns[idx+1]
            self.last_tags.append(tag)
            if tag == 'f':
                value = float(value)
            elif tag == 'i':
                value = int(value)
            # elif tag == 'b':
            #     ColorTerminal().warn("[OscAsciiFile] 'b' tag encountered; currently not supported")
            # else: # if tag =='s' ## assume tring
            #     value = str(value)
            self.last_data.append(value)
            idx += 2

        return True

    def write_line(self, addr, tags, data, time=0.0):
        # Line format (each value separated by a comma)
        # - timestamp
        # - OSC message address string, ie. "/some/message" (without quotes)
        # - param1 type
        # - param1 value
        # - param2 type
        # - param2 value
        # - etc. etc.
        columns = [str(time), addr]

        try:
            for idx, tag in enumerate(tags):
                columns.append(tag)
                columns.append(str(data[idx]))
        except IndexError:
            ColorTerminal().error("OscAsciiFile.write_line: fewer data values than tags given")

        self.write_file.write(self._separation_character.join(columns)+"\n")
