import pysimpledmx
import time,math

class Led:
	def __init__(self):
		self.running = False
		self.dmx = None
		self.connected = False
		self.config_file = None
		self.cfgprefix = 'py2030.led'

	def setup(self):
		from py2030.config_file import ConfigFile
		self.config_file = ConfigFile.instance()
		del ConfigFile
		self.config_file.load()
		self.config = self.config_file.get_value(self.cfgprefix)
		self.running = True
		# dmx.clear()
		# dmx.render() # render all of the above changes onto the DMX network


	def update(self):
		# val = int((math.sin(time.time()*0.5)*0.5+0.5)*255)
		# print(val)
		if self.dmx:
			self.dmx.setChannel(2, val, autorender=True)


	def connect(self):
		device = self.config_file.get_value(self.cfgprefix+'.led_device', default_value='/dev/cu.usbserial-EN187350')
		try:
			# https://pypi.python.org/pypi/pysimpledmx
			self.dmx = pysimpledmx.DMXConnection(device)
			self.connected = True
			return True
		except Exception as err:
			print "could not connect to DMX: ", err
			self.connected = False
		return self.connected

	def disconnect(self):
		self.dmx = None

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
