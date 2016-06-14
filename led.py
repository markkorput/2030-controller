import pysimpledmx
import time,math

dmx = pysimpledmx.DMXConnection('/dev/cu.usbserial-EN187350')

# mydmx.setChannel(1, 255) # set DMX channel 1 to full
# mydmx.setChannel(2, 128) # set DMX channel 2 to 128
# mydmx.setChannel(3, 0) # set DMX channel 3 to 0
# dmx.setChannel(1, 0)
# dmx.setChannel(2, 255)
# dmx.setChannel(3, 0)
# dmx.setChannel(4, 0)
# dmx.setChannel(2,255)
dmx.clear()
dmx.render() # render all of the above changes onto the DMX network

while True:
    val = int((math.sin(time.time()*0.5)*0.5+0.5)*255.0)
    print(val)
    dmx.setChannel(2, val, autorender=True)
    time.sleep(0.1)
