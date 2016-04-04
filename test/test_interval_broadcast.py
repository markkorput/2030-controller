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
        self.assertIsNone(self.interval_broadcast._data())
        self.assertEqual(self.interval_broadcast._interval(), 5.0)

if __name__ == '__main__':
    unittest.main()
