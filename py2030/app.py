from py2030.utils.color_terminal import ColorTerminal
from py2030.interface import Interface
from py2030.interval_broadcast import IntervalBroadcast
from py2030.outputs.osc import Osc
from py2030.config_file import ConfigFile
from py2030.http_server import HttpServer
from py2030.config_broadcaster import ConfigBroadcaster

class App:
    def __init__(self, options = {}):
        # attributes
        self.config_file = ConfigFile.instance()
        self.profile = 'client'

        self.config_file_monitor = None
        self.midi_effect_input = None

        self.interface = Interface.instance() # use global interface singleton instance
        self.interval_broadcast = None
        self.broadcast_osc_output = None
        self.http_server = None
        self.config_broadcaster = None # ConfigBroadcaster()

        # configuration
        self.options = {}
        self.configure(options)

        # autoStart is True by default
        if not 'setup' in options or options['setup']:
            self.setup()

    def __del__(self):
        self.destroy()

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)
        if 'profile' in options:
            self.profile = options['profile']
            ColorTerminal().green('Profile: '+self.profile)

    def setup(self):
        # read config file content
        self.config_file.load()
        # apply config data
        self._apply_config(self.config_file)

        self.config_file.dataChangeEvent += self._onConfigDataChange

    def _onConfigDataChange(self, data, config_file):
        ColorTerminal().yellow('config change: {0}'.format(data))
        self._apply_config(self.config_file)

    def destroy(self):
        if self.broadcast_osc_output:
            self.broadcast_osc_output.stop()
            self.broadcast_osc_output = None

        # stop monitoring config file file system changes
        if self.config_file_monitor and self.config_file_monitor.started:
            self.config_file_monitor.stop()

        # unregister from config file data change events
        if self.config_file and self._onConfigDataChange in self.config_file.dataChangeEvent:
            self.config_file.dataChangeEvent -= self._onConfigDataChange

        # stop http server
        if self.http_server:
            self.http_server.stop()
            self.http_server = None

    def update(self):
        if self.midi_effect_input:
            self.midi_effect_input.update()

        if self.interval_broadcast:
            self.interval_broadcast.update()

    def _apply_config(self, config_file):
        profile_data = config_file.get_value('py2030.profiles.'+self.profile)
        print 'Profile Data: ', profile_data

        #
        # Config File Monitor
        #
        if 'monitor_config' in profile_data and profile_data['monitor_config']:
            if self.config_file_monitor:
                if self.config_file_monitor.started:
                    pass
                else:
                    self.config_file_monitor.start()
            else:
                from py2030.config_file_monitor import ConfigFileMonitor
                self.config_file_monitor = ConfigFileMonitor(self.config_file, start=True)
        else:
            if self.config_file_monitor and self.config_file_monitor.started:
                self.config_file_monitor.stop()

        #
        # midi input
        #
        port = profile_data['midi_input_port'] if 'midi_input_port' in profile_data else None
        if port >= 0:
            if self.midi_effect_input:
                if self.midi_effect_input.port != port:
                    self.midi_effect_input.destroy()
                    self.midi_effect_input.port = port
                    # start receiving incoming midi message and map them to effect events
                    self.midi_effect_input.setup()
                else:
                    if not self.midi_effect_input.connected:
                        self.midi_effect_input.setup()
            else:
                from py2030.inputs.midi import MidiEffectInput
                self.midi_effect_input = MidiEffectInput({'port': port, 'setup': True})
        else:
            if self.midi_effect_input:
                self.midi_effect_input.destroy()

        # #
        # # OSC Broadcast/Multicast output
        # #
        # opts = {'autoStart': True}
        #
        # if self.config_file.get_value('py2030.multicast_ip'):
        #     opts['host'] = self.config_file.get_value('py2030.multicast_ip')
        # elif self.config_file.get_value('py2030.broadcast_ip'):
        #     opts['host'] = self.config_file.get_value('py2030.broadcast_ip')
        #
        # if self.config_file.get_value('py2030.multicast_port'):
        #     opts['port'] = self.config_file.get_value('py2030.multicast_port')
        #
        # if not self.broadcast_osc_output:
        #     self.broadcast_osc_output = Osc(opts)
        # else:
        #     self.broadcast_osc_output.configure(opts)
        #
        # #
        # # Interval broadcaster
        # #
        # interval = self.config_file.get_value('py2030.controller.broadcast_interval')
        # if (not interval or interval <= 0) and self.interval_broadcast:
        #     self.interval_broadcast = None
        #     ColorTerminal().yellow('broadcast interval disabled')
        #
        # if interval and interval > 0:
        #     if self.interval_broadcast:
        #         self.interval_broadcast.configure({'interval': interval})
        #         ColorTerminal().yellow('set broadcast interval to {0}'.format(interval))
        #     else:
        #         self.interval_broadcast = IntervalBroadcast({'interval': interval, 'data': 'TODO: controller info JSON'})
        #         ColorTerminal().yellow('started broadcast interval at {0}'.format(interval))
        #
        # #
        # # http server
        # #
        # port = self.config_file.get_value('py2030.controller.http_port')
        # if port:
        #     if self.http_server and self.http_server.port != port:
        #         # stop running http server
        #         self.http_server.stop()
        #         self.http_server = None
        #
        #     # if server not initialized already (or just shutdown)
        #     if not self.http_server:
        #         # start http server on (new) port
        #         self.http_server = HttpServer({'port': port})
        #         self.http_server.start()
        # elif not port and self.http_server:
        #     self.http_server.stop()
        #
