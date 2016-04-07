import test_helper
from py2030.utils.osc_broadcast_server import OscBroadcastServer
from py2030.outputs.osc import Osc as OscOutput
from py2030.dependencies.OSC import OSCServer

import unittest, time

class TestOscBroadcastServer(unittest.TestCase):

    # @classmethod
    # def setUpClass(cls):
    #     # this happens only once for the whole test-suite
    #     cls.server = OscBroadcastServer(('224.0.0.251', 1234))
    #
    # def setUp(self):
    #     # this happens before each test
    #     self.server = self.__class__.server

    def test_OSCServer_failure(self):
        server1 = OSCServer(('224.0.0.251', 1234))
        with self.assertRaisesRegexp(Exception, ".+Address already in use$"):
            server2 = OSCServer(('224.0.0.251', 1234))
        server1.close()

    def test_multiple_servers_on_same_ip_and_port(self):
        # setup; create 2 servers listening to the same ip and port
        self.server1 = OscBroadcastServer(('224.0.0.251', 1234))
        self.server2 = OscBroadcastServer(('224.0.0.251', 1234))
        self.server1.handle_timeout = self._onTimeout1
        self.server2.handle_timeout = self._onTimeout2
        self.server1.addMsgHandler('/packet', self._onPacket1)
        self.server2.addMsgHandler('/packet', self._onPacket2)
        self.received_on_server1 = []
        self.received_on_server2 = []
        # now let's create client to send some stuff osc_output
        osc_output = OscOutput({'host': '224.0.0.251', 'port': 1234})

        # before
        self.assertEqual(self.server1.server_address, self.server2.server_address) # ip and port
        self.assertEqual(self.received_on_server1, [])
        self.assertEqual(self.received_on_server2, [])

        # send two packages
        osc_output._sendMessage('/packet', ['foo'])
        osc_output._sendMessage('/packet', ['bar'])
        # receive first packets on both server instances
        self.server1.timed_out = False
        self.server1.handle_request()
        self.server2.timed_out = False
        self.server2.handle_request()
        # receive 2nd packets on both server instances
        self.server1.timed_out = False
        self.server1.handle_request()
        self.server2.timed_out = False
        self.server2.handle_request()

        # after
        self.assertEqual(self.received_on_server1, self.received_on_server2)
        self.assertEqual(self.received_on_server1[0][0], '/packet')
        self.assertEqual(self.received_on_server1[0][1], 's')
        self.assertEqual(self.received_on_server1[0][2], ['foo'])
        self.assertEqual(self.received_on_server1[1][2], ['bar'])

    def _onTimeout1(self):
        self.server1.timed_out=True
    def _onTimeout2(self):
        self.server2.timed_out=True
    def _onPacket1(self, addr, tags, data, client_address):
        self.received_on_server1.append((addr, tags, data, client_address))
    def _onPacket2(self, addr, tags, data, client_address):
        self.received_on_server2.append((addr, tags, data, client_address))


    def _onOscMessage(self, message, osc_output):
        self.sent_messages.append(message)


if __name__ == '__main__':
    unittest.main()
