import test_helper

# from py2030.module import ModuleClass
controllerModule = __import__('2030-controller')

import unittest, os, time

import threading

class Test2030Controller(unittest.TestCase):

    def setUp(self):
        # self.fixture1_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fixtures', 'fixture1'))
        self.launcher = controllerModule.Launcher()

    def test_run_and_stop(self):
        # create separate thread to run launcher's main loop
        thread = threading.Thread(target=self._threadMain)
        # verify launcher isn't running yet
        self.assertFalse(self.launcher.running)
        # start thread
        thread.start()
        # verify that the thread is alive
        self.assertTrue(thread.isAlive())
        # verify that the launcher is running
        self.assertTrue(self.launcher.running)
        # tell launcher to stop
        self.launcher.stop()
        # give the thread a ms to finish
        time.sleep(0.001)
        # verify launcher is not running anymore
        self.assertFalse(self.launcher.running)
        # verify thread has ended as well
        self.assertFalse(thread.isAlive())

    def _threadMain(self):
        # run the launcher's main loop (this will loop forever until requested to stop)
        self.launcher.run()

if __name__ == '__main__':
    unittest.main()
