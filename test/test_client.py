import test_helper

from py2030.client import Client
from py2030.controller import Controller
from py2030.interface import Interface
from py2030.outputs.osc import Osc as OscOutput

import unittest

class TestClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # this happens only once for the whole TestLauncher test-suite
        cls.client = Client()

    def setUp(self):
        # this happens before each test
        self.client = self.__class__.client

    def test_osc_connection(self):
        # setup
        controller = Controller()
        # before
        self.assertEqual(self.client.broadcast_osc_input.unknownMessageEvent.counter, 0)
        # broadcast invalid osc message from controller
        controller.broadcast_osc_output._sendMessage('/foobar')
        # update client (should update its osc broadcast listener)
        self.client.update()
        # after
        self.assertEqual(self.client.broadcast_osc_input.unknownMessageEvent.counter, 1)


if __name__ == '__main__':
    unittest.main()
