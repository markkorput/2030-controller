import test_helper
from py2030.config_file import ConfigFile

import unittest, os, time

class TestConfigFile(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # this happens only once for the whole TestLauncher test-suite
        path = os.path.join(os.path.dirname(__file__), 'fixtures', 'dummy_config_file.txt')
        cls.config_file = ConfigFile({'path': path})
        cls.content = "foo\nbar"
        # reset content, in case a test failed at the last run
        cls.config_file.write(cls.content)

    def setUp(self):
        # this happens before each test
        self.config_file = self.__class__.config_file
        self.content = self.__class__.content

    def test_read(self):
        self.assertEqual(self.config_file.read(), self.content)

    def test_write(self):
        # before
        f = open(self.config_file.path(), 'r')
        content = f.read()
        f.close()
        self.assertEqual(content, self.content)
        # change content
        newcontent = "If you see this, TestConfigFile.test_write failed. Please remove this first line\nfoo\nbar"
        self.config_file.write(newcontent)
        # after
        f = open(self.config_file.path(), 'r')
        content = f.read()
        f.close()
        self.assertEqual(content, newcontent)
        # cleanup; change content back
        self.config_file.write(self.content)

    def folder_path(self):
        self.assertEqual(self.config_file.folder_path(), './fixtures/')

    def test_monitoring(self):
        # setup
        self.config_file.start_monitoring()
        # before
        self.assertEqual(self.config_file.fileChangeEvent.counter, 0)
        # change content
        f = open(self.config_file.path(), 'w')
        content = f.write('TextConfigFile.text_monitoring failed again...')
        f.close()
        # give the monitoring thread some time to pick up on the file change
        time.sleep(0.5)
        # change content back
        f = open(self.config_file.path(), 'w')
        content = f.write("foo\nbar")
        f.close()
        # give the monitoring thread some time to pick up on the file change
        time.sleep(0.7)
        # after
        self.assertEqual(self.config_file.fileChangeEvent.counter, 2)

if __name__ == '__main__':
    unittest.main()
