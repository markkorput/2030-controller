from test_helper import EventLog
from py2030.outputs.output import Output
from py2030.interface import Interface

import unittest

class TestOutput(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # this happens only once for the whole TestLauncher test-suite
        cls.output = Output()

    def setUp(self):
        # ths happens before each individual test
        self.output = self.__class__.output

    def test_interface(self):
        # uses interface's singleton instance by default
        self.assertEqual(self.output.interface, Interface.instance())
        # lets caller configure interfacec attribute through interface option
        i1 = Interface()
        self.assertEqual(Output({'interface': i1}).interface, i1)

    def test_output(self):
        # setup
        eventlog = EventLog(self.output.outputEvent)
        self.output.interface.changes.clear()
        # before
        self.assertEqual(eventlog.count, 0)
        # by default, outputs all of its interface's changes models
        self.output.interface.changes.create()
        self.output.interface.changes.create({'some': 'data'})
        self.output.interface.broadcasts.create({'ip': 'localhost'})
        # after
        self.assertEqual(eventlog.count, 3)
        self.assertEqual(eventlog[0], (self.output.interface.changes[0], self.output))
        self.assertEqual(eventlog[1], (self.output.interface.changes[1], self.output))
        self.assertEqual(eventlog[2], (self.output.interface.changes[2], self.output))
        self.assertEqual(eventlog[2][0].data, {'data': {'ip': 'localhost'}, 'type': 'broadcasts', 'method': 'create'})


if __name__ == '__main__':
    unittest.main()
