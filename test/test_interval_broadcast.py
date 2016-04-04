import test_helper

from py2030.interval_broadcast import IntervalBroadcast
from py2030.interface import Interface

import unittest

class TestIntervalBroadcast(unittest.TestCase):

    def setUp(self):
        self.interval_broadcast = IntervalBroadcast()

    def test_defaults(self):
        # uses by default the singleton interface instance
        self.assertEqual(self.interval_broadcast.interface, Interface.instance())
        self.assertIsNone(self.interval_broadcast.data())
        self.assertEqual(self.interval_broadcast.interval(), 5.0)

    def test_manual_broadcast(self):
        # setup
        self.interval_broadcast.interface.broadcasts.clear()
        # before
        self.assertEqual(len(self.interval_broadcast.interface.broadcasts), 0)
        # perform manual broadcasts
        self.interval_broadcast.broadcast()
        self.interval_broadcast.broadcast()
        self.interval_broadcast.broadcast()
        # after
        self.assertEqual(len(self.interval_broadcast.interface.broadcasts), 3)

    def test_automatic_broadcasts(self):
        # setup
        broadcaster = IntervalBroadcast({'interval': 3.0})
        broadcaster.interface.broadcasts.clear()
        # before
        self.assertEqual(len(broadcaster.interface.broadcasts), 0)
        # fast forward 30 seconds
        broadcaster.update(30.0)
        # after; in 30.0 seconds accumulates to 10 intervals of 3.0 seconds
        self.assertEqual(len(broadcaster.interface.broadcasts), 10)



if __name__ == '__main__':
    unittest.main()
