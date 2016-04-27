import test_helper
from py2030.config_file import ConfigFile
from py2030.config_file_monitor import ConfigFileMonitor

import unittest, os, time

class TestConfigFileMonitor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # this happens only once for the whole TestLauncher test-suite
        path = os.path.join(os.path.dirname(__file__), 'fixtures', 'dummy.yaml')
        cls.config_file = ConfigFile({'path': path})
        cls.content = "foo:\n  bar: 'nothing'"
        # reset content, in case a test failed at the last run
        cls.config_file.write(cls.content)
        cls.monitor = ConfigFileMonitor(cls.config_file)

    def setUp(self):
        # this happens before each test
        self.config_file = self.__class__.config_file
        self.content = self.__class__.content
        self.monitor = self.__class__.monitor

    @unittest.skip("ConfigFileMonitor test disabled because of hard-to-test threading issue")
    def test_monitoring(self):
        self.monitor.start()

        self.assertEqual(self.config_file.dataChangeEvent.counter, 0)
        # change content
        f = open(self.config_file.path(), 'w')
        content = f.write('TextConfigFile.text_monitoring failed again...')
        f.close()
        # # give the monitoring thread some time to pick up on the file change
        t1 = time.time()
        while time.time() - t1 < 1:
            if self.config_file.dataChangeEvent.counter == 1:
                break
            time.sleep(0.1)
        self.assertEqual(self.config_file.dataChangeEvent.counter, 1)
        # change content back
        f = open(self.config_file.path(), 'w')
        content = f.write(self.content)
        f.close()
        # give the monitoring thread some time to pick up on the file change
        t1 = time.time()
        while time.time() - t1 < 1:
            if self.config_file.dataChangeEvent.counter == 2:
                break
            time.sleep(0.1)
        self.assertEqual(self.config_file.dataChangeEvent.counter, 2)

        self.monitor.stop()

if __name__ == '__main__':
    unittest.main()
