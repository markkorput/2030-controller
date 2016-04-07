import test_helper
from launcher import Launcher
from py2030.config_file import ConfigFile

import unittest, time

import threading

class TestLauncher(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # this happens only once for the whole TestLauncher test-suite
        cls.launcher = Launcher()
        cls.client_launcher = Launcher({'argv': ['--client']})
        cls.config_file = ConfigFile.instance()
        cls.config_file.load()

    def setUp(self):
        # this happens before each test
        self.launcher = self.__class__.launcher
        self.client_launcher = self.__class__.client_launcher
        self.config_file =self.__class__.config_file

    def test_controller(self):
        # setup
        c = self.launcher.controller
        # assert
        self.assertTrue(c.broadcast_osc_output.running)
        self.assertEqual(c.broadcast_osc_output.host(), self.config_file.get_value('py2030.multicast_ip'))
        self.assertEqual(c.broadcast_osc_output.port(), self.config_file.get_value('py2030.multicast_port'))
        self.assertEqual(c.interval_broadcast.interval(), self.config_file.get_value('py2030.controller.broadcast_interval'))

    def test_client(self):
        # setup
        c = self.client_launcher.client
        # assert
        self.assertTrue(c.broadcast_osc_input.running)
        self.assertTrue(c.broadcast_osc_input.connected)
        self.assertEqual(c.broadcast_osc_input.host(), '127.0.0.1') # default
        self.assertEqual(c.broadcast_osc_input.multicast(), self.config_file.get_value('py2030.multicast_ip'))
        self.assertEqual(c.broadcast_osc_input.port(), self.config_file.get_value('py2030.multicast_port'))


if __name__ == '__main__':
    unittest.main()
