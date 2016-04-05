import test_helper
from py2030.interface import Interface

import unittest

class TestInterface(unittest.TestCase):

    # @classmethod
    # def setUpClass(cls):
    #     # this happens only once for the whole TestLauncher test-suite
    #     Interface._instance = None

    # def setUp(self):
    #     # ths happens before each individual test
    #     pass

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



if __name__ == '__main__':
    unittest.main()
