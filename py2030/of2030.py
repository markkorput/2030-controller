import os, time

class Of2030:
    def __init__(self, options={}):
        # attributes
        self.start_time = time.time()
        self.time = 0.0
        self.next_log_monitor_time = 0.0

        # defaults
        self.path = '/home/pi/of2030'
        self.log_monitor_interval = 15.0
        self.log_monitor_treshold = 20.0

        # configure
        self.options = {}
        self.configure(options)

    def configure(self, options):
        previous_options = self.options
        self.options.update(options)

        if 'log_monitor_interval' in options:
            self.log_monitor_interval = options['log_monitor_interval']

        if 'log_monitor_treshold' in options:
            self.log_monitor_treshold = options['log_monitor_treshold']

        if 'path' in options:
            self.path = options['path']

    def update(self, dt=None):
        if dt:
            self.time = self.time + dt
        else:
            self.time = time.time() - self.start_time

        if self.time >= self.next_log_monitor_time:
            self.log_monitor()
            self.next_log_monitor_time = self.time + int(self.log_monitor_interval)

    def log_monitor(self):
        of_log_path = self._get_of2030_log_path()
        if not of_log_path:
            print "of2030 log file not found"
            self.spawn_in_background()
            return True

        # check if log file's modify timestamp has gotten too old
        # which we assume to mean that of2030 is not running anymore
        mtime = os.path.getmtime(of_log_path)
        mtime = time.time() - mtime
        if mtime > self.log_monitor_treshold:
            print "of2030 log.txt got too old (s): ", mtime
            self.spawn_in_background()
            return True

        return False

    def _get_of2030_log_path(self):
        p = self.path + '/bin/data/log.txt'
        if os.path.isfile(p):
            return p
        return None

    def _get_of2030_binary_path(self):
        if 'bin_path' in self.options:
            p = self.options['bin_path']
            if os.path.isfile(p):
                return p

        p = self.path + '/bin/of2030'
        if os.path.isfile(p):
            return p

        p = self.path + '/bin/of2030_debug'
        if os.path.isfile(p):
            return p

        return None

    def spawn_in_background(self):
        cmd = self._get_of2030_binary_path()

        if not cmd:
            print "Could not find of2030 executable (neither debug nor release version), can't spawn"
            return

        # no blocking; run in background
        cmd = cmd + " &"

        print '[Of2030] spawning of2030 process with command:', cmd
        os.system(cmd)
