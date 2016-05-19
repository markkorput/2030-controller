from datetime import datetime

class AliveNotifier:
    def __init__(self, options = {}):
        self.file = options['file'] if 'file' in options else None
        self.interval = options['interval'] if 'interval' in options else 10.0
        self.start_time = datetime.now()
        self.time = 0.0
        self.next_notify_time = 0.0

    def update(self, dt=None):
        if dt:
            self.time = self.time + dt
        else:
            self.time = (datetime.now() - self.start_time).total_seconds()

        if self.time >= self.next_notify_time:
            self.notify()
            self.next_notify_time = self.time + int(self.interval)

    def notify(self):
        if not self.file:
            print "[AliveNotifier] no file specified, can't notify"
            return

        timestamp =  datetime.strftime(datetime.now(),'%Y-%m-%d %H:%M:%S')
        f = open(self.file, 'w')
        f.write(timestamp)
        f.close()
