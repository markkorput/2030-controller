import test_helper
from py2030.client import Client
from py2030.controller import Controller

import unittest

class TestInterface(unittest.TestCase):

    # @classmethod
    # def setUpClass(cls):
    #     # this happens only once for the whole TestLauncher test-suite
    #     cls.client = Client()

    def setUp(self):
        # this happens before each test
        self.client = Client()

    def test_osc_connection(self):
        pass

if __name__ == '__main__':
    unittest.main()
