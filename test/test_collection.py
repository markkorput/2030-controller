import test_helper
from py2030.collections.collection import Collection
from py2030.collections.model import Model
from py2030.collections.broadcast import Broadcast

import unittest

class TestCollection(unittest.TestCase):

    # @classmethod
    # def setUpClass(cls):
    #     # this happens only once for the whole TestLauncher test-suite
    #     Interface._instance = None

    def setUp(self):
        # ths happens before each individual test
        self.collection = Collection()

    def test_getModelClass(self):
        # before
        self.assertEqual(Collection.model, Model)
        self.assertEqual(self.collection.model, None)
        self.assertEqual(self.collection.getModelClass(), Collection.model)
        # change
        self.collection.model = Broadcast
        # after
        self.assertEqual(Collection.model, Model)
        self.assertEqual(self.collection.model, Broadcast)
        self.assertEqual(self.collection.getModelClass(), Broadcast)

    def test_create(self):
        self.assertEqual(len(self.collection.models), 0)
        self.collection.create()
        self.assertEqual(len(self.collection.models), 1)
        self.collection.create({'data': 'foo'})
        self.assertEqual(len(self.collection.models), 2)
        self.collection.create({'age': 90})
        self.assertEqual(len(self.collection.models), 3)
        self.assertEqual(self.collection.models[0].get('data'), None)
        self.assertEqual(self.collection.models[1].get('data'), 'foo')
        self.assertEqual(self.collection.models[2].get('age'), 90)

    def test_add(self):
        model = self.collection.create({'id': 101})
        self.assertEqual(len(self.collection.models), 1)
        self.assertEqual(model.get('id'), 101)
        # add it two more times (chain notation)
        self.collection.add(model).add(model)
        self.assertEqual(len(self.collection.models), 3)
        # verify all three models are the actually the same
        self.assertEqual(self.collection[0], self.collection[1])
        self.assertEqual(self.collection[1], self.collection.models[2])

    def test_clear(self):
        # before
        self.assertEqual(len(self.collection.models), 0)
        # action
        self.collection.create()
        self.collection.create()
        self.assertEqual(len(self.collection.models), 2)
        self.collection.clear()
        # after
        self.assertEqual(len(self.collection.models), 0)

    def test_newModelEvent(self):
        # before
        self.assertEqual(self.collection.newModelEvent.counter, 0)
        # action
        self.collection.create()
        self.collection.create()
        self.collection.create()
        self.collection.create()
        # after
        self.assertEqual(self.collection.newModelEvent.counter, 4)

    def test_ClearEvent(self):
        # before
        self.assertEqual(self.collection.clearEvent.counter, 0)
        # action
        self.collection.clear()
        self.collection.create()
        self.collection.clear()
        self.collection.clear()
        # after
        self.assertEqual(self.collection.clearEvent.counter, 3)

if __name__ == '__main__':
    unittest.main()
