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
        self.of2030 = Of2030(path=self.ofpath)

    def ofparentfolder(self):
        return '/'.join(self.ofpath.split('/')[0:-1])

    def offoldername(self):
        return self.ofpath.split('/')[-1]

    def ofshadersfolder(self):
        return self.ofpath+'/bin/data/shadersES2'

class Of2030:
    def __init__(self, config_file=None, path=None):
        self.config_file = config_file
        self.path = path

        # grab path from config file?
        if self.config_file and not self.path:
            self.path = config_file.get_value('py2030.of2030.path', '/home/pi/of2030')

        self.bin_path = self.path + '/bin'
        self.data_path = self.path + '/bin/data'
        self.raspi_shaders_folder_path = self.path + '/bin/data/shadersES2'
        self.osc_path = self.path + '/bin/data/osc'

class Tool:
    def __init__(self):
        self.config_file = self._get_config_file()
        self.remotes = self._get_remotes()

    # local methods

    def _get_config_file(self):
        cf = ConfigFile({'path': 'config/tool.yaml'})
        cf.load()
        return cf

    def _get_remotes(self):
        remotes = []
        remotes_config = self.config_file.get_value('py2030.remotes', {})
        remote_names = remotes_config.keys()
        remote_names.sort()

        for remote_name in remote_names:
            remotes.append(Remote(remote_name, self.config_file))
        return remotes

    def _get_of_builder_remote(self):
        for remote in self.remotes:
            # print 'trying', remote.name, ' - ', remote.ofbuilder
            if remote.ofbuilder:
                return remote
        return None

    # py2030

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

    # local of2030

    def get_local_of_tar(self):
        tarfile = 'of2030.tar.gz'
        folder = Of2030(config_file=self.config_file).path
        ShellScript('data/scripts/of2030_tar_create.sh').execute({'tarfile': tarfile, 'folder': folder})

    # local of2030 src

    def get_local_ofsrc_tar(self):
        tarfile = 'of2030-src.tar.gz'
        folder = Of2030(config_file=self.config_file).path
        ShellScript('data/scripts/of2030src_tar_create.sh').execute({'tarfile': tarfile, 'folder': folder})

    def push_ofsrc_tar(self, builders_only=True):
        for remote in self.remotes:

            if builders_only and not remote.ofbuilder:
                # skip non-builder
                continue

            ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
            if not ssh.connect():
                # could not connect to current remote, move to next one
                continue

            tarfile='of2030-src.tar.gz'
            offolder=remote.of2030.path
            cmd = ShellScript('data/scripts/of2030src_tar_install.sh').get_script({'tarfile': tarfile, 'offolder': offolder})

            # push package
            ssh.put(tarfile, tarfile)
            # install package
            ssh.cmd(cmd)
            # remove package
            ssh.cmd('rm '+tarfile)
            # done for this remote
            ssh.disconnect()

    # local of2030 xml

    def get_local_ofxml_tar(self):
        tarfile = 'of2030-xml.tar.gz'
        folder = Of2030(config_file=self.config_file).path
        ShellScript('data/scripts/of2030xml_tar_create.sh').execute({'tarfile': tarfile, 'folder': folder})

    def push_ofxml_tar(self):
        for remote in self.remotes:
            ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
            if not ssh.connect():
                # could not connect to current remote, move to next one
                continue

            tarfile = 'of2030-xml.tar.gz'
            offolder=remote.of2030.path
            cmd = ShellScript('data/scripts/of2030xml_tar_install.sh').get_script({'tarfile': tarfile, 'offolder': offolder})

            # push package
            ssh.put(tarfile, tarfile)
            # install package
            ssh.cmd(cmd)
            # remove package
            ssh.cmd('rm '+tarfile)
            # done for this remote
            ssh.disconnect()


    # raspi of2030 build

    def fetch_of_build(self):
        remote = self._get_of_builder_remote()

        if not remote:
            print 'could not find ofbuilder-enabled remote'
            return False

        ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
        if not ssh.connect():
            # abort
            return False

        tarfile = 'of2030.tar.gz'

        # package bin folder into tar.gz file
        ssh.cmd(ShellScript('data/scripts/of2030_tar_create.sh').get_script({'tarfile': tarfile, 'folder': remote.ofpath}))
        # fetch package
        ssh.get(tarfile)
        # remove remotely
        ssh.cmd('rm '+tarfile)

    def push_of_build(self, skip_builders=True, builders_only=False):
        for remote in self.remotes:
            if remote.ofbuilder and skip_builders:
                # skip builder
                continue

            if builders_only and not remote.ofbuilder:
                # skip non-builder
                continue

            ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
            if not ssh.connect():
                # could not connect to current remote, move to next one
                continue

            tarfile='of2030.tar.gz'
            location=remote.ofparentfolder()
            # folder='of2030-'+time.strftime('%Y%m%d_%H%M%S')
            ss = ShellScript('data/scripts/of2030_tar_install.sh')
            installcmd = ss.get_script({'tarfile': tarfile, 'location': location, 'client_id': remote.name})
            ss = ShellScript('data/scripts/of2030_tar_install_restore_build_files.sh')
            restorecmd = ss.get_script({'location': location})

            # push package
            ssh.put(tarfile, tarfile)
            # install package
            ssh.cmd(installcmd)
            if builders_only:
                ssh.cmd(restorecmd)
            # remove package
            ssh.cmd('rm '+tarfile)
            # done for this remote
            ssh.disconnect()

    # control remote processes

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

    # shaders

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

    # OSC

    def get_osc(self, folder=None):
        # foler not specified by caller?
        if not folder:
            # try to get osc_folder setting from config file
            folder = self.config_file.get_value('py2030.osc_folder', None)
        # folder not specified in config file?
        if not folder:
            # use default osc folder of local of2030 folder
            folder = Of2030(self.config_file).osc_path

        tarfile = 'osc.tar.gz'
        ShellScript('data/scripts/osc_tar_create.sh').execute({'tarfile': tarfile, 'folder': folder})

    def push_osc(self):
        for remote in self.remotes:
            ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
            if not ssh.connect():
                # could not connect to current remote, move to next one
                continue

            tarfile='osc.tar.gz'
            location=remote.of2030.osc_path

            # push package
            ssh.put(tarfile, tarfile)
            # install package
            ssh.cmd(ShellScript('data/scripts/osc_tar_install.sh').get_script({'tarfile': tarfile, 'location': location}))
            # remove package
            ssh.cmd('rm '+tarfile)
            # done for this remote
            ssh.disconnect()

    # run generic command(s) on all remotes

    def cmd_all_remotes(self, cmd, wait=True):
        for remote in self.remotes:
            ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
            if not ssh.connect():
                # could not connect to current remote, move to next one
                continue

            ssh.cmd(cmd, wait)
            ssh.disconnect()


def main(opts, args):
    tool = Tool()

    # of2030

    if opts.update_of:
        tool.fetch_of_build()
        tool.push_of_build(skip_builders=True, builders_only=False)
        tarfile='of2030.tar.gz'
        print 'DONE, removing local copy;', tarfile
        subprocess.call(['rm', tarfile])

    if opts.get_of:
        tool.fetch_of_build()

    if opts.push_of:
        tool.push_of_build(skip_builders=True, builders_only=False)

    if opts.get_local_of:
        tool.get_local_of_tar()

    if opts.push_local_of:
        tool.push_of_build(skip_builders=False, builders_only=True)

    if opts.update_local_of:
        tool.get_local_of_tar()
        tool.push_of_build(skip_builders=False, builders_only=True)
        tarfile='of2030.tar.gz'
        print 'DONE, removing local copy;', tarfile
        subprocess.call(['rm', tarfile])

    if opts.get_ofsrc:
        tool.get_local_ofsrc_tar()

    if opts.push_ofsrc:
        tool.push_ofsrc_tar()

    if opts.update_ofsrc:
        tool.get_local_ofsrc_tar()
        tool.push_ofsrc_tar()
        tarfile='of2030-src.tar.gz'
        print 'DONE, removing local copy;', tarfile
        subprocess.call(['rm', tarfile])

    if opts.get_ofxml:
        tool.get_local_ofxml_tar()

    if opts.push_ofxml:
        tool.push_ofxml_tar()

    if opts.update_ofxml:
        tool.get_local_ofxml_tar()
        tool.push_ofxml_tar()
        tarfile='of2030-xml.tar.gz'
        print 'DONE, removing local copy;', tarfile
        subprocess.call(['rm', tarfile])

    # of2030/bin/data/osc (presets)

    if opts.get_osc:
        tool.get_osc(opts.folder)

    if opts.push_osc:
        tool.push_osc()

    if opts.update_osc:
        tool.get_osc(opts.folder)
        tool.push_osc()
        tarfile = 'osc.tar.gz'
        print 'DONE, removing local copy;', tarfile
        subprocess.call(['rm', tarfile])

    # of2030/bin/data/shadersES2

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

    # py2030
    if opts.get_py:
        # create_py_tar
        tarfile='py2030.tar.gz'
        ShellScript('data/scripts/py2030_tar_create.sh').execute({'tarfile': tarfile})

    if opts.push_py:
        tool.push_py()

    if opts.update_py:
        # create_py_tar
        tarfile='py2030.tar.gz'
        ShellScript('data/scripts/py2030_tar_create.sh').execute({'tarfile': tarfile})

        tool.push_py()

        tarfile='py2030.tar.gz'
        print 'DONE, removing local copy;', tarfile
        subprocess.call(['rm', tarfile])

    # rpi of2030 and py2030 control

    if opts.stop:
        tool.stop()
    if opts.start:
        tool.start()

    if opts.restart:
        tool.restart()

    if opts.start_of:
        tool.cmd_all_remotes('make RunDebug -C of2030', False)

    # rpi system

    if opts.reboot:
        tool.cmd_all_remotes('sudo reboot')

    if opts.shutdown:
        tool.cmd_all_remotes('sudo shutdown -h now')

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()

    # actions
    parser.add_option('--shutdown', dest='shutdown', action="store_true", default=False)
    parser.add_option('--reboot', dest='reboot', action="store_true", default=False)

    parser.add_option('--stop', dest='stop', action="store_true", default=False)
    parser.add_option('--start', dest='start', action="store_true", default=False)
    parser.add_option('--restart', dest='restart', action="store_true", default=False)
    parser.add_option('--start-of', dest='start_of', action="store_true", default=False)

    parser.add_option('--get-of', dest='get_of', action="store_true", default=False)
    parser.add_option('--push-of', dest='push_of', action="store_true", default=False)
    parser.add_option('--update-of', dest='update_of', action="store_true", default=False)

    parser.add_option('--get-local-of', dest='get_local_of', action="store_true", default=False)
    parser.add_option('--push-local-of', dest='push_local_of', action="store_true", default=False)
    parser.add_option('--update-local-of', dest='update_local_of', action="store_true", default=False)

    parser.add_option('--get-ofxml', dest='get_ofxml', action="store_true", default=False)
    parser.add_option('--push-ofxml', dest='push_ofxml', action="store_true", default=False)
    parser.add_option('--update-ofxml', dest='update_ofxml', action="store_true", default=False)

    parser.add_option('--get-ofsrc', dest='get_ofsrc', action="store_true", default=False)
    parser.add_option('--push-ofsrc', dest='push_ofsrc', action="store_true", default=False)
    parser.add_option('--update-ofsrc', dest='update_ofsrc', action="store_true", default=False)

    parser.add_option('--get-py', dest='get_py', action="store_true", default=False)
    parser.add_option('--push-py', dest='push_py', action="store_true", default=False)
    parser.add_option('--update-py', dest='update_py', action="store_true", default=False)

    parser.add_option('--get-shaders', dest='get_shaders', action="store_true", default=False)
    parser.add_option('--push-shaders', dest='push_shaders', action="store_true", default=False)
    parser.add_option('--update-shaders', dest='update_shaders', action="store_true", default=False)

    parser.add_option('--get-osc', dest='get_osc', action="store_true", default=False)
    parser.add_option('--push-osc', dest='push_osc', action="store_true", default=False)
    parser.add_option('--update-osc', dest='update_osc', action="store_true", default=False)

    # params
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
