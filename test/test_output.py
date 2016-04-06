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

    def test_accept_types(self):
        #setup
        out = Output({'accept_types': ['type1', 'type3']})
        eventlog = EventLog(out.outputEvent)
        #type1 changes are accepted
        out.interface.changes.create({'type': 'type1'})
        self.assertEqual(eventlog.count, 1)
        self.assertEqual(eventlog[0][0].get('type'), 'type1')
        #type2 changes not accepted
        out.interface.changes.create({'type': 'type2'})
        self.assertEqual(eventlog.count, 1)
        #type3 changes are accepted
        out.interface.changes.create({'type': 'type3'})
        self.assertEqual(eventlog.count, 2)
        self.assertEqual(eventlog[1][0].get('type'), 'type3')
        #foo-type changes not accepted
        out.interface.changes.create({'type': 'foo'})
        self.assertEqual(eventlog.count, 2)

    def test_ignore_types(self):
        #setup
        out = Output({'ignore_types': ['ignored1', 'ignored2']})
        eventlog = EventLog(out.outputEvent)
        #type1 changes are accepted
        out.interface.changes.create({'type': 'type1'})
        self.assertEqual(eventlog.count, 1)
        self.assertEqual(eventlog[0][0].get('type'), 'type1')
        #ignored1 changes not accepted
        out.interface.changes.create({'type': 'ignored1'})
        self.assertEqual(eventlog.count, 1)
        #type3 changes are accepted
        out.interface.changes.create({'type': 'type3'})
        self.assertEqual(eventlog.count, 2)
        self.assertEqual(eventlog[1][0].get('type'), 'type3')
        #foo-type changes not accepted
        out.interface.changes.create({'type': 'ignored2'})
        self.assertEqual(eventlog.count, 2)

    def test_both_ignored_and_accepted_will_be_ignored(self):
        out = Output({'ignore_types': ['t1'], 'accept_types': ['t1']})
        out.interface.changes.create({'type': 't1'})
        self.assertEqual(out.outputEvent.counter, 0)


if __name__ == '__main__':
    unittest.main()
