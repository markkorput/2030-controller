from py2030.utils.color_terminal import ColorTerminal
# from py2030.utils.event import Event

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
        self.currentFrame = None
        self.currentFrameTime = None
        self.currentFrameIndex = -1

        # other attribute(s)
        self._separation_character = ','

        # events
        # self.loopEvent = Event()

    def __del__(self):
        self.stop()

    def start_reading(self):
        self.stopReading()

        try:
            if not self.path or self.path == 'auto':
                self.path = 'data/ascii_osc_file.csv'

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

    def set_loop(self, loop):
        self.loop = loop

    def nextFrame(self):
        pass
        # bytecount = self._readFrameSize() # int: bytes
        # self.currentFrameTime = self._readFrameTime() # float: seconds
        #
        # if bytecount == None or self.currentFrameTime == None:
        #     return None
        #
        # self.currentFrame = self.read_file.read(bytecount)
        # self.currentFrameIndex += 1
        #
        # return self.currentFrame

    def _readFrameSize(self):
        pass
        # # int is 4 bytes
        # value = self.read_file.read(4)
        #
        # # end-of-file?
        # if not value:
        #     if not self.loop:
        #         return None
        #
        #     # reset file handle
        #     self.read_file.seek(0)
        #     self.currentFrame = None
        #     self.currentFrameTime = None
        #     self.currentFrameIndex = -1
        #     # notify
        #     self.loopEvent(self)
        #     # try again
        #     return self._readFrameSize()
        #
        # # 'unpack' 4 binary bytes into integer
        # return struct.unpack('i', value)[0]

    def _readFrameTime(self):
        pass
        # # float of 4 bytes
        # value = self.read_file.read(4)
        #
        # # end-of-file?
        # if not value:
        #     # TODO; raise format error?
        #     return None
        #
        # # 'unpack' 4 binary bytes into float
        # return struct.unpack('f', value)[0]

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
