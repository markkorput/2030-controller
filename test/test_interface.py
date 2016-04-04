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

if __name__ == '__main__':
    unittest.main()
