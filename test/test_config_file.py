import test_helper
from py2030.config_file import ConfigFile

import unittest, os, time

class TestConfigFile(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # this happens only once for the whole TestLauncher test-suite
        path = os.path.join(os.path.dirname(__file__), 'fixtures', 'dummy.yaml')
        cls.config_file = ConfigFile({'path': path})
        cls.content = "foo:\n  bar: 'nothing'"
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
        elif os.path.isfile('config/config.yaml.default'):
            self.assertEqual(instance.path(), 'config/config.yaml.default')
        elif os.path.isfile('../config/config.yaml.default'):
            self.assertEqual(instance.path(), '../config/config.yaml.default')

    def test_read(self):
        self.assertEqual(self.config_file.read(), self.content)

    def test_read_fails(self):
        self.assertEqual(ConfigFile({'path': 'i-dont-exist.yaml'}).read(), None)

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

    def test_exists(self):
        self.assertFalse(ConfigFile({'path': 'foo/bar/idontexist.json'}).exists())
        self.assertTrue(ConfigFile({'path': __file__}).exists())

    def test_load(self):
        # new instance for same file
        config_file = ConfigFile({'path': self.config_file.path()})
        # before (doesn't auto-load by default)
        self.assertEqual(config_file.data, None)
        # load
        config_file.load()
        # after
        self.assertEqual(config_file.data, {'foo': {'bar': 'nothing'}})

    def test_load_skipped(self):
        # new instance for same file
        config_file = ConfigFile({'path': self.config_file.path()})
        config_file.data = {}
        self.assertEqual(config_file.data, {})
        # load
        config_file.load()
        # after; didn't reload
        self.assertEqual(config_file.data, {})

    def test_load_forced(self):
        # new instance for same file
        config_file = ConfigFile({'path': self.config_file.path()})
        config_file.data = {}
        self.assertEqual(config_file.data, {})
        # load
        config_file.load({'force': True})
        # after; didn't reload
        self.assertEqual(config_file.data, {'foo': {'bar': 'nothing'}})

if __name__ == '__main__':
    unittest.main()
