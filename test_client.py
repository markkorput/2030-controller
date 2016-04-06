from py2030.outputs.osc import Osc
from py2030.collections.change import Change
import time


if __name__ == '__main__':
    osc = Osc({'host':'224.0.0.251', 'port': 1234})
    while True:
        change = Change({'foo': 'bar', 't': str(time.time())})
        osc._onNewChangeModel(change, None)
        time.sleep(1)
