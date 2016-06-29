#!/usr/bin/env python
import time
from rtmidi.midiutil import open_midiport

from py2030.utils.color_terminal import ColorTerminal
from py2030.interface import Interface
from py2030.config_file import ConfigFile

class MidiEffectInput:
    def __init__(self, options = {}):
        # params
        self.options = options
        # attributes
        self.port = self.options['port'] if 'port' in self.options else None
        self.interface = self.options['interface'] if 'interface' in self.options else Interface.instance()
        self.config_file = ConfigFile.instance()
        self.midiin = None
        self.port_name = None
        self.limit = 10
        self.connected = False

        # # setup
        # if 'setup' in options and options['setup']:
        #     self.setup()

    def __del__(self):
        self.destroy()

    def setup(self):
        # get the data we need from the config file
        self.midi_effect_map = self._get_midi_effect_map()
        # start listening for midi messages
        # (we'll poll for new message in the update method)
        self._connect()
        # reset timer
        self.time = 0
        self.op_map = self.options['map'] if 'map' in self.options else {}

    def destroy(self):
        if self.midiin:
            self._disconnect()

    def verbose(self):
        return 'verbose' in self.options and self.options['verbose']

    def _get_midi_effect_map(self):
        # get the part of the config file data we need
        mapping_data = self.config_file.get_value('py2030.midi_triggers')
        if not mapping_data:
            ColorTerminal().warn('[MidiEffectInput] no midi triggers configured')
            return {}

        # collect mapping data in here and return it
        midi_effect_map = {}

        for midi_note_number in mapping_data:
            # this midi note configured to trigger an effect?
            if 'effect' in mapping_data[midi_note_number]:
                # add the effect data (array) in our midi effect map
                midi_effect_map[midi_note_number] = mapping_data[midi_note_number]['effect']

        return midi_effect_map

    def _connect(self):
        try:
            self.midiin, self.port_name = open_midiport(self.port)
        except IOError as err:
            print "Failed to initialize MIDI interface:", err
            self.midiin = None
            self.port_name = None
            self.connected = False
            return
        except EOFError as err:
            print("Failed to initialize MIDI interface")
            self.midiin = None
            self.port_name = None
            self.connected = False
            return
        print("Midi input initialized on port: " + self.port_name)
        self.connected = True
        return

    def _disconnect(self):
        self.midiin.close_port()
        self.midiin = None
        self.connected = False

    def update(self):
        if not self.midiin:
            return

        for i in range(self.limit):
            # get next incoming midi message
            msg = self.midiin.get_message()
            # no more messages; we're done

            if not msg:
                return

            if self.verbose():
                print 'midi message: ', msg # ie. ([176, 12, 7], 0.0)
                # print self.op_map # ie. {'176': {'4': {'op': 'led'}}}

            self.time += msg[1]

            if msg[0][0] in self.op_map:
                opmap = self.op_map[msg[0][0]]
                if msg[0][1] in opmap:
                    opmap=opmap[msg[0][1]]
                    if 'osc' in opmap:
                        self.interface.oscMessageEvent(opmap['osc'], [], [], None)
                        if self.verbose():
                            print 'mapped to', opmap['osc']

            # else:
            # # process message
            # effect_data = self.midi_message_to_effect(msg[0])
            # # if effect_data:
            #     # self.interface.effectEvent(effect_data)
            #     # print('[MidiEffectInput] triggered interface effectEvent with: ', effect_data)


            # debugging
            # print("[%s] @%0.6f %r" % (self.port_name, self.time, message))

    def midi_message_to_effect(self, midi_message):
        # is this a noteOn midi message?
        if midi_message[0] == 144:
            # de we have an effect for this note number?
            if midi_message[1] in self.midi_effect_map:
                return self.midi_effect_map[midi_message[1]]

        return None




# for manual testing this python file can be invoked directly
if __name__ == '__main__':
    mt = MidiInput()

    print("Entering main loop. Press Control-C to exit.")
    try:
        while True:
            mt.update()
            time.sleep(0.01)
    except KeyboardInterrupt:
        print('Keyboard Interrupt')

    del mt
