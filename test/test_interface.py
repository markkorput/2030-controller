import test_helper
from py2030.interface import Interface

import unittest

class TestInterface(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # this happens only once for the whole TestLauncher test-suite
        cls.interface = Interface()

    def setUp(self):
        # ths happens before each individual test
        self.interface = self.__class__.interface

    def test_singleton_instance(self):
        # get singleton instance
        instance = Interface.instance()
        # before; singleton instance initialized and equal to returned instance
        self.assertIsNotNone(Interface._instance)
        self.assertEqual(instance, Interface._instance)

    def test_newModelEvent(self):
        # setup
        instance = Interface()
        instance.newModelEvent += self._onNewModel
        # before
        self.assertEqual(instance.newModelEvent.counter, 0)
        # action; this should first the interface's newModelEvent
        instance.broadcasts.create()
        instance.broadcasts.create({'abc': 'xyz'})
        # after
        self.assertEqual(instance.newModelEvent.counter, 2)

    def _onNewModel(self, model, collection, interface):
        # should be an Interface object
        self.assertEqual(interface.__class__, Interface)
        # should be from the interface's broadcast class
        self.assertEqual(collection, interface.broadcasts)
        # should be the last model of the collection
        self.assertEqual(model, collection.models[-1])

    # changes is technically 'just' another collection in the interface,
    # but it has a special role; all changes (new model/updated model/removed movel)
    # to any of the other collections cause a changes model to be created
    # the change model's data dict can be serialized and deserialized into/from a json format
    def test_changes(self):
        # setup
        self.interface.changes.clear()
        # create changes
        self.interface.changes.create()
        self.assertEqual(len(self.interface.changes), 1)
        # create another change inside the interface (add a broadcast model)
        self.interface.broadcasts.create({'foo': 'bar'})
        # should result in again a new changes model
        self.assertEqual(len(self.interface.changes), 2)
        self.assertEqual(self.interface.changes[1].data, {'method': 'create', 'type': 'broadcasts', 'data': {'foo': 'bar'}})

    def test_updates(self):
        # setup
        self.interface.broadcasts.clear()
        # before
        self.assertEqual(len(self.interface.broadcasts), 0)
        # add 'create broadcast' update
        self.interface.updates.create({'method': 'create', 'type': 'broadcasts', 'data': {'foo': 'bar', 'footender': 'bartender'}})
        # result
        self.assertEqual(len(self.interface.broadcasts), 1)
        self.assertEqual(self.interface.broadcasts[0].data, {'foo': 'bar', 'footender': 'bartender'})

    def test_add_master(self):
        # setup
        interface1 = Interface()
        interface2 = Interface()
        # before
        self.assertEqual(len(interface2.broadcasts), 0)
        # action
        interface1.broadcasts.create({'id': 111})
        interface1.broadcasts.create({'id': 222})
        interface2.add_master(interface1)
        interface1.broadcasts.create({'id': 333})
        interface1.broadcasts.create({'id': 444})
        # after
        self.assertEqual(len(interface2.broadcasts), 2)
        self.assertEqual(interface2.broadcasts[0].get('id'), 333)
        self.assertEqual(interface2.broadcasts[1].get('id'), 444)


if __name__ == '__main__':
    unittest.main()
