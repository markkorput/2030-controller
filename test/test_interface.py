import test_helper
from py2030.interface import Interface

import unittest

class TestInterface(unittest.TestCase):

    def setUp(self):
        # self.interface = Interface()
        pass

    def test_singleton_instance(self):
        # before; singleton instance not initialized
        self.assertIsNone(Interface._instance)
        # get singleton instance
        instance = Interface.instance()
        # before; singleton instance initialized and equal to returned instance
        self.assertIsNotNone(Interface._instance)
        self.assertEqual(instance, Interface._instance)

if __name__ == '__main__':
    unittest.main()
