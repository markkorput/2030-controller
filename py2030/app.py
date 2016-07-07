from py2030.utils.color_terminal import ColorTerminal
from py2030.interface import Interface
from py2030.config_file import ConfigFile

import copy
from datetime import datetime

# from py2030.client_side.client_info import ClientInfo

class App:
    def __init__(self, options = {}):
        print "\n\n--------------------------------------- PY2030 -- " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # attributes
        self.config_file = ConfigFile.instance()
        self.profile = 'client'
        self.profile_data = {}
        self.queue = []
        self.joined = False

        # components
        self.update_components = []
        self.__host_info_cache = None
        self.alive_notifier = None
        self.interface = Interface.instance() # use global interface singleton instance
        self.version_packager = None
        self.config_file_monitor = None
        self.midi_effect_input = None
        self.osc_outputs = []
        self.joined_osc_outputs = []
        self.osc_inputs = []
        self.http_server = None
        self.interval_broadcast = None
        self.interval_joiner = None
        self.config_broadcaster = None
        self.downloader = None
        self.syncer = None
        self.osc_ascii_input = None

        # configuration
        self.options = {}
        self.configure(options)

        self.interface.joinEvent += self._onJoin
        self.interface.ackEvent += self._onAck

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
        # self._apply_config(self.config_file)

        # don't do apply config directly; add an instruction to the queue,
        # so it gets process in the update loop
        self.queue.append('reconfig')

    def destroy(self):
        for osc_output in self.osc_outputs:
            osc_output.stop()
        self.osc_outputs = []

        for osc_output in self.joined_osc_outputs:
            osc_output.stop()
        self.joined_osc_outputs = []

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

        if hasattr(self, 'config_recorders'):
            for cfgrec in self.config_recorders:
                cfgrec.stop()

    def update(self):
        for comp in self.update_components:
            comp.update()

        if self.alive_notifier:
            self.alive_notifier.update()

        for instruction in self.queue:
            if instruction == 'reconfig':
                self._apply_config(self.config_file)
        self.queue = []

        for osc_input in self.osc_inputs:
            osc_input.update()

        if self.midi_effect_input:
            self.midi_effect_input.update()

        if self.interval_joiner:
            self.interval_joiner.update()

        if self.interval_broadcast:
            self.interval_broadcast.update()

        if self.osc_ascii_input:
            self.osc_ascii_input.update()

    def _apply_config(self, config_file):
        profile_data = config_file.get_value('py2030.profiles.'+self.profile)
        if not profile_data:
            profile_data = {}
        self.profile_data = profile_data
        # print 'Profile Data: ', profile_data

        #
        # alive-notifier
        #
        if 'alive_notifier' in profile_data:
            from py2030.alive_notifier import AliveNotifier
            self.alive_notifier = AliveNotifier(profile_data['alive_notifier'])
            del AliveNotifier

        #
        # Of2030
        #
        if 'of2030' in profile_data:
            if hasattr(self, 'of2030'):
                self.update_components.remove(self.of2030)
                del self.of2030

            from py2030.of2030 import Of2030
            self.of2030 = Of2030(profile_data['of2030'])
            self.update_components.append(self.of2030)
            del Of2030

        #
        # Version Packager
        #
        if 'version_packager' in profile_data:
            from py2030.version_packager import VersionPackager
            opts = profile_data['version_packager']
            opts.update({'version': self._version()})
            self.version_packager = VersionPackager(opts)
            self.version_packager.package()
            del VersionPackager

        #
        # Config File Monitor
        #
        if 'monitor_config' in profile_data and profile_data['monitor_config']:
            if self.config_file_monitor:
                if not self.config_file_monitor.started:
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
        if 'midi_input' in profile_data:
            from py2030.inputs.midi import MidiEffectInput
            self.midi_effect_input = MidiEffectInput(profile_data['midi_input'])
            self.midi_effect_input.setup()

            del MidiEffectInput

        if 'hoh_vid_starter' in profile_data:
            from py2030.hoh_vid_starter import HohVidStarter
            self.hoh_vid_starter = HohVidStarter(profile_data['hoh_vid_starter'])
            self.hoh_vid_starter.setup()
            del HohVidStarter

        #     if self.midi_effect_input:
        #         if self.midi_effect_input.port != port:
        #             self.midi_effect_input.destroy()
        #             self.midi_effect_input.port = port
        #             # start receiving incoming midi message and map them to effect events
        #             self.midi_effect_input.setup()
        #         else:
        #             if not self.midi_effect_input.connected:
        #                 self.midi_effect_input.setup()
        #     else:
        #         from py2030.inputs.midi import MidiEffectInput
        #         self.midi_effect_input = MidiEffectInput(mid)
        #         del MidiEffectInput
        # else:
        #     if self.midi_effect_input:
        #         self.midi_effect_input.destroy()

        #
        # OSC outputs
        #
        if 'osc_outputs' in profile_data:
            from py2030.outputs.osc import Osc as OscOutput

            # stop and destroy existing osc outputs
            for osc in self.osc_outputs:
                osc.stop()
            self.osc_outputs = []

            for data in profile_data['osc_outputs'].values():
                # this profile is for joining clients, don't initialize statically
                if not 'ip' in data or data['ip'] != 'joiner':
                    self.osc_outputs.append(OscOutput(data)) # auto-starts

            del OscOutput

        #
        # OSC inputs
        #
        if 'osc_inputs' in profile_data:
            from py2030.inputs.osc import Osc as OscInput

            # stop and destroy existing osc inputs
            for osc_input in self.osc_inputs:
                osc_input.stop()
            self.osc_inputs = []

            for data in profile_data['osc_inputs'].values():
                if 'ip' in data and data['ip'] == 'self':
                    data['ip'] = self._ip()
                self.osc_inputs.append(OscInput(data)) # auto-starts

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
                self.http_server = HttpServer({'port': port, 'host_info': self._host_info()})
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
        if 'downloader' in profile_data:
            opts = profile_data['downloader']
            if self.downloader:
                self.downloader.configure(opts)
            else:
                from py2030.client_side.downloader import Downloader
                self.downloader = Downloader(opts)
                self.downloader.setup()
                del Downloader
        else:
            if self.downloader:
                self.downloader.destroy()
                self.downloader = None

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
                self.interval_broadcast = IntervalBroadcast({'interval': interval, 'data': {'ip': self._ip(), 'role': 'controller', 'version': config_file.get_value('py2030.version')}})
                ColorTerminal().yellow('started broadcast interval at {0}'.format(interval))
                del IntervalBroadcast

        #
        # Interval joiner
        #
        interval = profile_data['join_interval'] if 'join_interval' in profile_data else None
        if (not interval or interval <= 0) and self.interval_joiner:
            self.interval_joiner = None
            ColorTerminal().yellow('joiner interval disabled')

        if interval and interval > 0:
            if self.interval_joiner:
                self.interval_joiner.configure({'interval': interval})
                ColorTerminal().yellow('set joiner interval to {0}'.format(interval))
            else:
                from py2030.client_side.interval_joiner import IntervalJoiner
                # TODO; determine port from osc listeners?
                self.interval_joiner = IntervalJoiner({'interval': interval, 'data': {'ip': self._ip(), 'port': self._join_data_port(), 'hostname': self._hostname()}})
                ColorTerminal().yellow('started joiner interval at {0}'.format(interval))
                del IntervalJoiner

        #
        # Syncer
        #
        if 'syncer' in profile_data:
            from py2030.syncer import Syncer
            self.syncer = Syncer(profile_data['syncer'])
            self.syncer.setup()
            del Syncer

        #
        # OscAscii recorder
        #
        if 'osc_ascii_output' in profile_data:
            from py2030.outputs.osc_ascii import OscAscii
            self.osc_ascii_output = OscAscii(profile_data['osc_ascii_output'])
            if 'file' in self.options:
                self.osc_ascii_output.configure({'path': self.options['file']})
            self.osc_ascii_output.start()
            del OscAscii

        if 'osc_ascii_input' in profile_data:
            from py2030.inputs.osc_ascii import OscAsciiInput
            self.osc_ascii_input = OscAsciiInput(profile_data['osc_ascii_input'])
            if 'file' in self.options:
                self.osc_ascii_input.configure({'path': self.options['file']})
            if 'loop' in self.options:
                self.osc_ascii_input.configure({'loop': self.options['loop']})
            self.osc_ascii_input.endEvent += self._onOscAsciiInputEnd
            self.osc_ascii_input.start()
            del OscAsciiInput

        #
        # Config recorder
        #
        if 'config_recorders' in profile_data:
            # initialize attribute
            if not hasattr(self, 'config_recorders'):
                self.config_recorders = []

            # cleanup existing recorders
            for cfgrec in self.config_recorders:
                cfgrec.stop()
            self.config_recorders = []

            # create recorders according to configuration profiles
            from py2030.config_recorder import ConfigRecorder
            for rec_profile in profile_data['config_recorders'].values():
                cfgrec = ConfigRecorder(rec_profile)
                cfgrec.start()
                self.config_recorders.append(cfgrec)
            del ConfigRecorder


        if 'led' in profile_data:
            led_opts = profile_data['led']
            led_opts['interface'] = self.interface
            from py2030.outputs.led import Led
            self.led_out = Led(led_opts)
            self.led_out.setup()



    # returns the port number to be send with the join dataChangeEvent
    # (this will be our incoming OSC port)
    def _join_data_port(self):
        # find the first osc input (listener) that accepts 'acks'
        for osc_input in self.osc_inputs:
            if osc_input.receivesType('ack'):
                return osc_input.port()
        # default
        return 2030

    def _host_info(self):
        if self.__host_info_cache:
            return self.__host_info_cache

        # import socket
        import subprocess
        platform = subprocess.Popen("uname", shell=True, stdout=subprocess.PIPE).stdout.read().strip()
        hostname = subprocess.Popen("hostname", shell=True, stdout=subprocess.PIPE).stdout.read().strip()

        if platform == 'Darwin': # Mac OSX
            import socket
            ip = socket.gethostbyname(hostname)
            del socket
        else: # linux
            ip = subprocess.Popen("hostname -I", shell=True, stdout=subprocess.PIPE).stdout.read().strip()

        del subprocess

        self.__host_info_cache = {'hostname': hostname, 'ip': ip, 'platform': platform}
        print 'host info: ', self.__host_info_cache
        return self.__host_info_cache

    def _ip(self):
        return self._host_info()['ip']

    def _hostname(self):
        return self._host_info()['hostname']

    def _getJoinerOscOutProfileData(self):
        # find osc output profile for joining clients
        if 'osc_outputs' in self.profile_data:
            for data in self.profile_data['osc_outputs'].values():
                # the 'ip' attribute must be 'joiner'
                if 'ip' in data and data['ip'] == 'joiner':
                    return copy.copy(data)
        return None

    def _version(self):
        return self.config_file.get_value('py2030.version')

    def _onJoin(self, join_data):
        joined_config = self._getJoinerOscOutProfileData()

        if not joined_config: # osc to joiners not enabled (the case for clients)
            # ColorTerminal().warn('osc-to-joiners not enabled')
            return

        # check we got all required params. TODO; require hostname as well?
        if not 'ip' in join_data or not 'port' in join_data or not 'hostname' in join_data:
            ColorTerminal().warn('Got incomplete join data (require ip, port and hostname)')
            print join_data
            return

        ack_data = {'version': self._version()}
        if self.http_server:
            ack_data['version_download_url'] = self.http_server.version_url(self._version())

        # don't register if already outputting to this address/port
        for out in self.osc_outputs:
            if out.host() == join_data['ip'] and out.port() == join_data['port']:
                # TODO trigger ackEvent on interface instead, with client id?
                out.trigger('ack', ack_data)
                ColorTerminal().warn('Got join with already registered osc-output specs')
                print join_data
                return

        # don't register if already outputting to this address/port
        for out in self.joined_osc_outputs:
            if out.host() == join_data['ip'] and out.port() == join_data['port']:
                # TODO trigger ackEvent on interface instead, with client id?
                out.trigger('ack', ack_data)
                ColorTerminal().warn('Got join with already registered osc-output specs')
                print join_data
                return

        # prep params
        joined_config['ip'] = join_data['ip']
        joined_config['client_id'] = join_data['hostname']
        if not 'port' in joined_config or joined_config['port'] == 'joiner':
            joined_config['port'] = join_data['port']

        from py2030.outputs.osc import Osc as OscOutput
        osc_out = OscOutput(joined_config)
        # TODO trigger ackEvent on interface instead, with client id?
        osc_out.trigger('ack', ack_data)
        self.joined_osc_outputs.append(osc_out) # auto-starts
        del OscOutput

    def _onAck(self, data):
        # controller side;
        # not triggered on controller-side (for now)

        # client side
        if self.interval_joiner and self.interval_joiner.running:
            ColorTerminal().yellow('Got ackEvent, stopping interval joiner')
            self.interval_joiner.stop()
        self.joined = True

        # self.downloader will take care of the rest

    def _onOscAsciiInputEnd(self, oscAsciiInput):
        self.interface.restartEvent()
