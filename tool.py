#!/usr/bin/env python
from py2030.config_file import ConfigFile
from py2030.utils.ssh_remote import SshRemote
from py2030.utils.shell_script import ShellScript
from scp import SCPClient
import time, subprocess

class Remote:
    def __init__(self, name, config_file):
        self.name = name
        self.config_file = config_file
        prefix = 'py2030.remotes.'+name
        self.ip = config_file.get_value(prefix+'.ip', None)
        self.hostname = config_file.get_value(prefix+'.hostname', name)
        self.ssh_username = config_file.get_value(prefix+'.ssh.usr', 'pi')
        self.ssh_password = config_file.get_value(prefix+'.ssh.psw', 'raspberry')
        self.ofbuilder = config_file.get_value(prefix+'.ofbuilder', False)
        self.ofpath = config_file.get_value(prefix+'.of2030.path', '/home/pi/openFrameworks/apps/of2030/of2030')

    def ofparentfolder(self):
        return '/'.join(self.ofpath.split('/')[0:-1])

    def offoldername(self):
        return self.ofpath.split('/')[-1]

    def ofshadersfolder(self):
        return self.ofpath+'/bin/data/shadersES2'

class Of2030:
    def __init__(self, config_file):
        self.config_file = config_file
        self.path = config_file.get_value('py2030.of2030.path', '/home/pi/of2030')
        self.raspi_shaders_folder_path = self.path + '/bin/data/shadersES2'

class Tool:
    def __init__(self):
        self.config_file = self.get_config_file()
        self.remotes = self.get_remotes()

    def get_config_file(self):
        cf = ConfigFile({'path': 'config/tool.yaml'})
        cf.load()
        return cf

    def get_remotes(self):
        remotes = []
        remotes_config = self.config_file.get_value('py2030.remotes', {})
        remote_names = remotes_config.keys()
        remote_names.sort()

        for remote_name in remote_names:
            remotes.append(Remote(remote_name, self.config_file))
        return remotes

    def get_of_builder_remote(self):
        for remote in self.remotes:
            # print 'trying', remote.name, ' - ', remote.ofbuilder
            if remote.ofbuilder:
                return remote
        return None

    def fetch_of_build(self):
        remote = self.get_of_builder_remote()

        if not remote:
            print 'could not find ofbuilder-enabled remote'
            return False

        ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
        if not ssh.connect():
            # abort
            return False

        tarfile = 'of2030-bin.tar.gz'

        # package bin folder into tar.gz file
        ssh.cmd(ShellScript('data/scripts/of2030_bin_tar_create.sh').get_script({'tarfile': tarfile, 'offolder': remote.ofpath}))
        # fetch package
        ssh.get(tarfile)
        # remove remotely
        ssh.cmd('rm '+tarfile)

    def push_of_build(self, skip_builders=True):
        for remote in self.remotes:
            if remote.ofbuilder and skip_builders:
                # we probably got the build form this raspi, skip it
                continue

            ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
            if not ssh.connect():
                # could not connect to current remote, move to next one
                continue

            tarfile='of2030-bin.tar.gz'
            location=remote.ofparentfolder()
            # folder='of2030-'+time.strftime('%Y%m%d_%H%M%S')

            # push package
            ssh.put(tarfile, tarfile)
            # install package
            ssh.cmd(ShellScript('data/scripts/of2030_bin_tar_install.sh').get_script({'tarfile': tarfile, 'location': location}))
            # remove package
            ssh.cmd('rm '+tarfile)
            # done for this remote
            ssh.disconnect()

    def create_py_tar(self):
        tarfile='py2030.tar.gz'
        ShellScript('data/scripts/py2030_tar_create.sh').execute({'tarfile': tarfile})

    def push_py(self):
        tarfile='py2030.tar.gz'
        folder='py2030-'+time.strftime('%Y%m%d_%H%M%S')
        installcmd = ShellScript('data/scripts/py2030_tar_install.sh').get_script({'tarfile': tarfile, 'folder': folder})

        for remote in self.remotes:
            ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
            if not ssh.connect():
                # could not connect to current remote, move to next one
                continue

            # push package
            ssh.put(tarfile, tarfile)
            # install package
            ssh.cmd(installcmd)
            # remove package
            ssh.cmd('rm '+tarfile)
            # done for this remote
            ssh.disconnect()

    def start(self):
        cmd = ShellScript('data/scripts/rpi_start.sh').get_script()

        for remote in self.remotes:
            ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
            if not ssh.connect():
                # could not connect to current remote, move to next one
                continue

            # restart processes
            ssh.cmd(cmd, wait=False)

    def stop(self):
        cmd = ShellScript('data/scripts/rpi_stop.sh').get_script()

        for remote in self.remotes:
            ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
            if not ssh.connect():
                # could not connect to current remote, move to next one
                continue

            # restart processes
            ssh.cmd(cmd, wait=False)

    def restart(self):
        startcmd = ShellScript('data/scripts/rpi_start.sh').get_script()
        stopcmd = ShellScript('data/scripts/rpi_stop.sh').get_script()

        for remote in self.remotes:
            ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
            if not ssh.connect():
                # could not connect to current remote, move to next one
                continue

            # restart processes
            ssh.cmd(startcmd, wait=False)
            ssh.cmd(stopcmd, wait=False)

    def get_shaders(self, folder=None):
        if not folder:
            folder = Of2030(self.config_file).raspi_shaders_folder_path

        tarfile = 'shadersES2.tar.gz'
        ShellScript('data/scripts/shaders_tar_create.sh').execute({'tarfile': tarfile, 'folder': folder})

    def push_shaders(self, skip_builders=False):
        for remote in self.remotes:
            if remote.ofbuilder and skip_builders:
                continue

            ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
            if not ssh.connect():
                # could not connect to current remote, move to next one
                continue

            tarfile='shadersES2.tar.gz'
            location=remote.ofshadersfolder()
            # push package
            ssh.put(tarfile, tarfile)
            # install package
            ssh.cmd(ShellScript('data/scripts/shaders_tar_install.sh').get_script({'tarfile': tarfile, 'location': location}))
            # remove package
            ssh.cmd('rm '+tarfile)
            # done for this remote
            ssh.disconnect()

def main(opts, args):
    tool = Tool()

    if opts.update_of:
        tool.fetch_of_build()
        tool.push_of_build()
        tarfile='of2030-bin.tar.gz'
        print 'DONE, removing local copy;', tarfile
        subprocess.call(['rm', tarfile])

    if opts.get_of:
        tool.fetch_of_build()

    if opts.push_of:
        tool.push_of_build()

    if opts.update_py:
        tool.create_py_tar()
        tool.push_py()
        tarfile='py2030.tar.gz'
        print 'DONE, removing local copy;', tarfile
        subprocess.call(['rm', tarfile])

    if opts.get_py:
        tool.create_py_tar()

    if opts.push_py:
        tool.push_py()

    if opts.stop:
        tool.stop()
    if opts.start:
        tool.start()

    if opts.restart:
        tool.restart()

    if opts.get_shaders:
        tool.get_shaders(opts.folder)

    if opts.push_shaders:
        tool.push_shaders()

    if opts.update_shaders:
        tool.get_shaders(opts.folder)
        tool.push_shaders()
        tarfile = 'shadersES2.tar.gz'
        print 'DONE, removing local copy;', tarfile
        subprocess.call(['rm', tarfile])

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('--get-of', dest='get_of', action="store_true", default=False)
    parser.add_option('--push-of', dest='push_of', action="store_true", default=False)
    parser.add_option('--update-of', dest='update_of', action="store_true", default=False)
    parser.add_option('--get-py', dest='get_py', action="store_true", default=False)
    parser.add_option('--push-py', dest='push_py', action="store_true", default=False)
    parser.add_option('--update-py', dest='update_py', action="store_true", default=False)
    parser.add_option('--stop', dest='stop', action="store_true", default=False)
    parser.add_option('--start', dest='start', action="store_true", default=False)
    parser.add_option('--restart', dest='restart', action="store_true", default=False)
    parser.add_option('--get-shaders', dest='get_shaders', action="store_true", default=False)
    parser.add_option('--push-shaders', dest='push_shaders', action="store_true", default=False)
    parser.add_option('--update-shaders', dest='update_shaders', action="store_true", default=False)
    parser.add_option('-f', '--folder', dest='folder', default=None)

    # parser.add_option('-c', '--client', dest='client', action="store_true", default=False)
    # parser.add_option('-f', '--file', dest='file', default=None)
    # parser.add_option('-l', '--loop', dest='loop', action="store_true", default=False)
    # parser.add_option('-t', '--threaded', dest='threaded', action="store_true", default=False)
    # parser.add_option('--install', dest='install', action="store_true", default=False)
    # parser.add_option('--bootstrap', dest='bootstrap', action="store_true", default=False)
    # parser.add_option('--route-ip', dest="route_ip", action="store_true", help="Route IP address (default: the controller profile's osc_out_ip value from the config file) to specific interface (default: en0)", default=None)
    options, args = parser.parse_args()
    del OptionParser
    main(options, args)
