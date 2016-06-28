import pysimpledmx
import time,math

class Led:
	def __init__(self, opts={}):
		self.options = opts
		self.dmx = None
		self.connected = False
		self.interface = opts['interface']
		self.device = opts['device'] if 'device' in opts else '/dev/cu.usbserial-EN187350'
		self.interface.ledValueEvent += self.onLedValue
		self.verbose = 'verbose' in opts and opts['verbose']
		self.channel_map = opts['channel_map'] if 'channel_map' in opts else {1: 1, 2: 2, 3: 3, 4: 4}

	def setup(self):
		self._connect()

	# def update(self):
	# 	# val = int((math.sin(time.time()*0.5)*0.5+0.5)*255)
	# 	# # print(val)
	# 	# if self.dmx:
	# 	#	 self.dmx.setChannel(2, val, autorender=True)
    #     pass

	def _connect(self):
		try:
			if self.verbose:
				print 'trying to connect to serial LED dmx device:', self.device
			# https://pypi.python.org/pypi/pysimpledmx
			self.dmx = pysimpledmx.DMXConnection(self.device)
			self.connected = True
			return True
		except Exception as err:
			print "could not connect to DMX: ", err
			self.connected = False
		return self.connected

	def _disconnect(self):
		self.dmx = None
		self.connected = False

	def mapped_channel(ch):
		if ch in self.channel_map:
			return self.channel_map[ch]
		return None

	def onLedValue(self, channel, val):
		# val = int((math.sin(time.time()*0.5)*0.5+0.5)*255)
		# # print(val)
		if self.dmx:
			ch = self.mapped_channel(channel)
			if ch:
				self.dmx.setChannel(ch, val, autorender=True)

		if self.verbose:
			print '[led-out]:', val

if __name__ == '__main__':
	led = Led()
	led.setup()
	# led.connect()
	try:
		while led.running:
			led.update()
			time.sleep(0.02)
	except KeyboardInterrupt:
		print 'KeyboardInterrupt. Quitting.'
