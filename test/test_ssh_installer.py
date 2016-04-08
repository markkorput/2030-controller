import test_helper

from py2030.ssh_installer import SshInstaller

import unittest

class TestSshInstaller(unittest.TestCase):

    def test_defaults(self):
        installer = SshInstaller('192.168.1.2', options={'connect': False})
        self.assertEqual(installer.ip, '192.168.1.2')
        self.assertEqual(installer.username, None)
        self.assertEqual(installer.password, None)
        self.assertEqual(installer.local_package_path, './py2030.zip')
        self.assertEqual(installer.package_name, 'py2030.zip')
        self.assertEqual(installer.folder_name, 'py2030')

    def test_custom_path(self):
        installer = SshInstaller(None, 'pi', 'raspberry', options={'connect': False, 'local_package_path': '../some/path/to/a_file.zip'})
        self.assertEqual(installer.username, 'pi')
        self.assertEqual(installer.password, 'raspberry')
        self.assertEqual(installer.local_package_path, '../some/path/to/a_file.zip')
        self.assertEqual(installer.package_name, 'a_file.zip')
        self.assertEqual(installer.folder_name, 'a_file')

if __name__ == '__main__':
    unittest.main()
