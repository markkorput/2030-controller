import paramiko, os, re, time, subprocess
from scp import SCPClient

from py2030.utils.color_terminal import ColorTerminal

class SshInstaller:
    def __init__(self, ip, username=None, password=None, options = {}):
        self.ip = ip
        self.username = username
        self.password = password
        self.options = options

        self.connected = False
        self.client = None

        self.local_package_path = self.options['local_package_path'] if 'local_package_path' in self.options else './py2030.zip'
        self.package_name = os.path.basename(self.local_package_path)
        self.folder_name = re.sub(r'.zip$', '', self.package_name)

        if(not 'connect' in options or options['connect'] == True):
            self._connect()

    # returns list of
    def ls(self):
        if hasattr(self, '_ls_cache'):
            return self._ls_cache
        stdin, stdout, stderr = self.client.exec_command('ls')

        self._ls_cache = []

        for line in stdout:
            self._ls_cache.append(str(line.strip('\n')))

        return self._ls_cache

    def remote_path_exists(self, remote_path):
        lines = self.ls()
        for line in lines:
            if line == remote_path:
                return True
        return False

    def put(self):
        ColorTerminal().blue('scp-ing {0} to {1}'.format(self.local_package_path, self.ip))

        with SCPClient(self.client.get_transport()) as scp:
            scp.put(self.local_package_path, self.package_name)

    def folder_exists(self):
        return self.remote_path_exists(self.folder_name)

    def backup_folder(self):
        lines = self.ls()
        number = 1

        while '{0}.bak.{1}'.format(self.folder_name, str(number).zfill(3)) in lines:
            number += 1

        new_name = '{0}.bak.{1}'.format(self.folder_name, str(number).zfill(3))
        ColorTerminal().blue('backing up existing folder on {0} to {1}'.format(self.ip, new_name))
        stdin, stdout, stderr = self.client.exec_command('mv {0} {1}'.format(self.folder_name, new_name))
        for line in stdout: pass

    def unpack_package(self):
        ColorTerminal().blue('unpacking {0} on {1}'.format(self.package_name, self.ip))
        stdin, stdout, stderr = self.client.exec_command('mkdir {0}'.format(self.folder_name))
        # wait?
        for line in stdout: pass
        for line in stderr: ColorTerminal().fail(str(line.strip('\n')))

        stdin, stdout, stderr = self.client.exec_command('unzip -o {0} -d {1}'.format(self.package_name, self.folder_name))
        # wait?
        for line in stdout: pass
        for line in stderr: ColorTerminal().fail(str(line.strip('\n')))

    def delete_package(self):
        ColorTerminal().blue('deleting {0} on {1}'.format(self.package_name, self.ip))
        stdin, stdout, stderr = self.client.exec_command('rm {0}'.format(self.package_name))
        for line in stdout: pass
        for line in stderr: ColorTerminal().fail(str(line.strip('\n')))

    def install(self, cd=True, bootstrap=True):
        if cd:
            self.client.exec_command('cd ~/{0}'.format(self.folder_name))
            for line in stdout: pass
            for line in stderr: ColorTerminal().fail(str(line.strip('\n')))

        # todo; install pip if necessary?

        self.client.exec_command('sudo pip install -r requirements.txt')
        for line in stdout: pass
        for line in stderr: ColorTerminal().fail(str(line.strip('\n')))

        if bootstrap:
            stdin, stdout, stderr = self.client.exec_command('./run2030.py --install --bootstrap')
        else:
            stdin, stdout, stderr = self.client.exec_command('./run2030.py --install')
        for line in stdout: pass
        for line in stderr: ColorTerminal().fail(str(line.strip('\n')))

    def start_remotely(self):
        # launch daemon
        pass

    def _connect(self):
        if self.connected:
            return None

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.client.connect(self.ip, username=self.username, password=self.password)
        except paramiko.ssh_exception.AuthenticationException as err:
            ColorTerminal().fail('[SshInstaller] ssh authentication failed on host {0}'.format(self.ip))
            self.connected = False
            return False

        ColorTerminal().blue('ssh connection established with {0}'.format(self.ip))
        self.connected = True
        return True

    def _disconnect(self):
        if self.connected:
            self.client.close()
            self.client = None

    def execute(self):
        zip_created = False

        if not os.path.isfile(os.path.abspath(self.local_package_path)):
            ColorTerminal().blue('[SshInstaller] creating local zip {0}'.format(self.local_package_path))
            subprocess.call(['zip', '-r', 'py2030.zip', '.', '-x', '.*'])
            zip_created = True

        self.put()
        if self.folder_exists():
            self.backup_folder()
        self.unpack_package()
        self.install(bootstrap=True)
        self.delete_package()

        if zip_created:
            ColorTerminal().blue('[SshInstaller] deleting local zip {0}'.format(self.local_package_path))
            subprocess.call(['rm', self.local_package_path])
