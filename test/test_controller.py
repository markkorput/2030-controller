import test_helper
from py2030.controller import Controller


import unittest, json

class TestController(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # this happens only once for the whole test-suite
        cls.controller = Controller()
        cls.controller.setup()

    def setUp(self):
        # this happens before each test
        self.controller = self.__class__.controller

    def test_osc_broadcast(self):
        # setup
        self.sent_messages = []
        self.controller.osc_output.messageEvent += self._onOscMessage

        # before
        self.assertEqual(len(self.sent_messages), 0)

        # do broadcasts
        self.controller.interval_broadcast.broadcast()
        self.controller.interface.broadcasts.create({'data': '123-test-check'})
        self.controller.interface.broadcasts.create()

        # after
        self.assertEqual(len(self.sent_messages), 3)
        self.assertEqual(json.loads(self.sent_messages[0][0]), {'data': 'TODO: controller info JSON'})
        self.assertEqual(json.loads(self.sent_messages[1][0]), {'data': '123-test-check'})
        self.assertEqual(json.loads(self.sent_messages[2][0]), {})

    def _onOscMessage(self, message, osc_output):
        self.sent_messages.append(message)


if __name__ == '__main__':
    unittest.main()
