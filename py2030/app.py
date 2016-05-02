from py2030.utils.color_terminal import ColorTerminal
from py2030.interface import Interface
from py2030.config_file import ConfigFile

# from py2030.client_side.client_info import ClientInfo

class App:
    def __init__(self, options = {}):
        # attributes
        self.config_file = ConfigFile.instance()
        self.profile = 'client'

        self.interface = Interface.instance() # use global interface singleton instance

        self.config_file_monitor = None
        self.midi_effect_input = None
        self.osc_output = None
        self.osc_inputs = []
        self.http_server = None

        self.interval_broadcast = None
        self.config_broadcaster = None
        self.reconfig_downloader = None

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
        # ColorTerminal().yellow('config change: {0}'.format(data))
        self._apply_config(self.config_file)

    def destroy(self):
        if self.osc_output:
            self.osc_output.stop()
            self.osc_output = None

        for osc_input in self.osc_inputs:
            osc_input.stop()
        self.osc_inputs = []

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
        for osc_input in self.osc_inputs:
            osc_input.update()

        if self.midi_effect_input:
            self.midi_effect_input.update()

        if self.interval_broadcast:
            self.interval_broadcast.update()

    def _apply_config(self, config_file):
        profile_data = config_file.get_value('py2030.profiles.'+self.profile)
        # print 'Profile Data: ', profile_data

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

        #
        # OSC output
        #
        port = profile_data['osc_out_port'] if 'osc_out_port' in profile_data else None
        ip = profile_data['osc_out_ip'] if 'osc_out_ip' in profile_data else None
        if ip and port:
            if self.osc_output:
                self.osc_output.configure({'port': port, 'host': ip})
                if not self.osc_output.running:
                    self.osc_output.start()
            else:
                from py2030.outputs.osc import Osc as OscOutput
                self.osc_output = OscOutput({'port': port, 'host': ip}) # auto-starts
        else:
            if self.osc_output:
                self.osc_output.stop()

        #
        # OSC inputs
        #
        if 'osc_inputs' in profile_data:
            from py2030.inputs.osc import Osc as OscInput

            # stop and destroy existing osc inputs
            for osc_input in self.osc_inputs:
                osc_input.stop()
            self.osc_inputs = []

            for osc_input_data in profile_data['osc_inputs'].values():
                try:
                    opts = {'port': osc_input_data['port']}
                    if 'shared' in osc_input_data and osc_input_data['shared']:
                        opts['multicast'] = osc_input_data['ip']
                    else:
                        opts['host'] = osc_input_data['ip']
                except:
                    ColorTerminal().fail("badly formed osc input data:")
                    print osc_input_data
                    continue

                self.osc_inputs.append(OscInput(opts)) # auto-starts

            del OscInput

        #
        # http server
        #
        port = profile_data['http_server_port'] if 'http_server_port' in profile_data else None
        if port:
            if self.http_server and self.http_server.port != port:
                # stop running http server
                self.http_server.stop()
                self.http_server = None

            # if server not initialized already (or just shutdown)
            if not self.http_server:
                # start http server on (new) port
                from py2030.http_server import HttpServer
                self.http_server = HttpServer({'port': port})
                self.http_server.start()
                del HttpServer

        elif not port and self.http_server:
            self.http_server.stop()

        #
        # Config broadcaster
        #
        enabled = profile_data['broadcast_reconfig'] if 'broadcast_reconfig' in profile_data else None
        if enabled:
            if not self.config_broadcaster:
                from py2030.config_broadcaster import ConfigBroadcaster
                self.config_broadcaster = ConfigBroadcaster()
                # del ConfigBroadcaster
        else:
            if self.config_broadcaster:
                self.config_broadcaster.destroy()
                self.config_broadcaster = None

        #
        # Reconfig Downloader
        #
        enabled = profile_data['download_reconfig'] if 'download_reconfig' in profile_data else None
        if enabled:
            if self.reconfig_downloader:
                self.reconfig_downloader.setup()
            else:
                from py2030.client_side.reconfig_downloader import ReconfigDownloader
                self.reconfig_downloader = ReconfigDownloader()
                self.reconfig_downloader.setup()
                del ReconfigDownloader
        else:
            if self.reconfig_downloader:
                self.reconfig_downloader.destroy()

        #
        # Interval broadcaster
        #
        interval = profile_data['broadcast_interval'] if 'broadcast_interval' in profile_data else None
        if (not interval or interval <= 0) and self.interval_broadcast:
            self.interval_broadcast = None
            ColorTerminal().yellow('broadcast interval disabled')

        if interval and interval > 0:
            if self.interval_broadcast:
                self.interval_broadcast.configure({'interval': interval})
                ColorTerminal().yellow('set broadcast interval to {0}'.format(interval))
            else:
                from py2030.interval_broadcast import IntervalBroadcast
                self.interval_broadcast = IntervalBroadcast({'interval': interval, 'data': 'TODO: controller info JSON'})
                ColorTerminal().yellow('started broadcast interval at {0}'.format(interval))
                del IntervalBroadcast
