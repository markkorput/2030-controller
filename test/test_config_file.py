import test_helper
from py2030.config_file import ConfigFile

import unittest, os, time

class TestConfigFile(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # this happens only once for the whole TestLauncher test-suite
        path = os.path.join(os.path.dirname(__file__), 'fixtures', 'dummy_config_file.txt')
        cls.config_file = ConfigFile({'path': path})
        cls.content = "{foo:'bar'}"
        # reset content, in case a test failed at the last run
        cls.config_file.write(cls.content)

    def setUp(self):
        # this happens before each test
        self.config_file = self.__class__.config_file
        self.content = self.__class__.content

    def test_default_paths(self):
        self.assertEqual(ConfigFile.default_paths, ('config/config.yaml', '../config/config.yaml', 'config/config.yaml.default', '../config/config.yaml.default'))

    def test_instance(self):
        # get singleton instance
        instance = ConfigFile.instance()
        # before; singleton instance initialized and equal to returned instance
        self.assertIsNotNone(ConfigFile._instance)
        self.assertEqual(instance, ConfigFile._instance)
        if os.path.isfile('config/config.yaml'):
            self.assertEqual(instance.path(), 'config/config.yaml')
        elif os.path.isfile('../config/config.yaml'):
            self.assertEqual(instance.path(), '../config/config.yaml')
        elif os.path.isfile('../config/config.yaml.default'):
            self.assertEqual(instance.path(), 'config/config.yaml.default')
        elif os.path.isfile('../config/config.yaml.default'):
            self.assertEqual(instance.path(), '../config/config.yaml.default')


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

    @unittest.skip("ConfigFile monitoring test disabled because of hard-to-test threading issue")
    def test_monitoring(self):
        # setup
        self.config_file.start_monitoring()
        # before
        self.assertEqual(self.config_file.changeDataEvent.counter, 0)
        # change content
        f = open(self.config_file.path(), 'w')
        content = f.write('TextConfigFile.text_monitoring failed again...')
        f.close()
        # # give the monitoring thread some time to pick up on the file change
        t1 = time.time()
        while time.time() - t1 < 1:
            if self.config_file.fileChangeEvent.counter == 1:
                break
            time.sleep(0.1)
        self.assertEqual(self.config_file.changeDataEvent.counter, 1)
        # change content back
        f = open(self.config_file.path(), 'w')
        content = f.write(self.content)
        f.close()
        # give the monitoring thread some time to pick up on the file change
        t1 = time.time()
        while time.time() - t1 < 1:
            if self.config_file.fileChangeEvent.counter == 2:
                break
            time.sleep(0.1)
        self.assertEqual(self.config_file.fileChangeEvent.counter, 2)

    def test_exists(self):
        self.assertFalse(ConfigFile({'path': 'foo/bar/idontexist.json'}).exists())
        self.assertTrue(ConfigFile({'path': __file__}).exists())

if __name__ == '__main__':
    unittest.main()
