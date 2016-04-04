import test_helper

from py2030.client import Client
from py2030.client import Interface
from py2030.outputs.osc import Osc as OscOutput

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
        # setup; create separate interface (simulating a different machine)
        other_interface = Interface()
        # initial situation; no broadcasts in client's interface
        self.assertEqual(len(self.client.interface.broadcasts), 0)
        # create broadcast on other interface
        other_interface.broadcasts.create()
        self.client.update()
        # verify nothing appeared yet in client's Interface
        self.assertEqual(len(self.client.interface.broadcasts), 0)
        # create osc output for other interface (client sets up osc input automatically)
        osc_output = OscOutput({'interface': other_interface})
        # verify default osc settings on both input and output match
        self.assertEqual(osc_output.host(), self.client.osc_input.host())
        self.assertEqual(osc_output.port(), self.client.osc_input.port())
        # now, with the osc connection established, again, create a broadcast on the other interface
        other_interface.broadcasts.create({'data': 'test-connection'})
        # check, once more, that the client's interface has no broadcasts (yet)
        self.assertEqual(len(self.client.interface.broadcasts), 0)
        # run update on client (which should in turn update its osc_input)
        self.client.update()
        # result; broadcast was received and added to client's interface
        self.assertEqual(len(self.client.interface.broadcasts), 1)
        self.assertEqual(self.client.interface.broadcasts[0].get('data'), 'test-connection')

if __name__ == '__main__':
    unittest.main()
