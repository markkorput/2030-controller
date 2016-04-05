import test_helper
from py2030.utils.event import Event

import unittest

class TestEvent(unittest.TestCase):

    # @classmethod
    # def setUpClass(cls):
    #     # this happens only once for the whole TestLauncher test-suite
    #     Interface._instance = None

    # def setUp(self):
    #     # ths happens before each individual test
    #     pass

    def test_counter(self):
        # setup
        event = Event()
        # before
        self.assertEqual(event.counter, 0)
        # two ays of firing the event
        event.fire()
        event()
        # after
        self.assertEqual(event.counter, 2)

    def test_queueing(self):
        # setup
        event = Event()
        # this callback is gonna add another callback
        # while the event is being fire, which -before queueing
        # caused a RuntimeError
        event += self._onEvent1
        # fire
        event.fire(event)
        # after; fire only once. The second callback was added during the fire event
        # which means in isn't included in that occurene of the event, because that
        # would cause complicated state situations
        self.assertEqual(event.counter, 1)

    def _onEvent1(self, event=None):
        # add a second callback, WHILE the event is being fired
        # this second callback won't be fired for this event's occurence
        if event:
            event += self._onEvent2

    def _onEvent2(self, event=None):
        # fire the event again, DURING another fire
        # note that this time we ommit the event param,
        # so we're not gonna get stuck in an endless cycle
        if event:
            event.fire()

if __name__ == '__main__':
    unittest.main()
