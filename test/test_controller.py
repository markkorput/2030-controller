from test_helper import EventLog
from py2030.controller import Controller


import unittest, json

class TestController(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # this happens only once for the whole test-suite
        cls.controller = Controller()

    def setUp(self):
        # this happens before each test
        self.controller = self.__class__.controller

    def test_osc_broadcast(self):
        # setup
        eventlog = EventLog(self.controller.broadcast_osc_output.messageEvent)
        # before
        self.assertEqual(eventlog.count, 0)
        # do broadcasts
        self.controller.interval_broadcast.broadcast()
        self.controller.interface.broadcasts.create({'data': '123-test-check'})
        self.controller.interface.broadcasts.create()
        # after
        self.assertEqual(eventlog.count, 3)

        self.assertEqual(eventlog[0][0][0], json.dumps({'method': 'create', 'type': 'broadcasts', 'data': {'data': 'TODO: controller info JSON'}}))
        self.assertEqual(eventlog[1][0][0], json.dumps({'method': 'create', 'type': 'broadcasts', 'data': {'data': '123-test-check'}}))
        self.assertEqual(eventlog[2][0][0], json.dumps({'method': 'create', 'type': 'broadcasts', 'data': {}}))

if __name__ == '__main__':
    unittest.main()
