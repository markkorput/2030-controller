import test_helper

# from py2030.module import ModuleClass
controllerModule = __import__('2030-controller')

import unittest
import os

class Test2030Controller(unittest.TestCase):

    def setUp(self):
        # self.fixture1_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fixtures', 'fixture1'))
        self.launcher = controllerModule.Launcher()
        pass

    def test_initial_frame(self):
        # self.assertIsNone(None)
        self.assertFalse(self.launcher.isRunning())

if __name__ == '__main__':
    unittest.main()
