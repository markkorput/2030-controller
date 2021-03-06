#!/usr/bin/env python
from py2030.config_file import ConfigFile
from py2030.utils.ssh_remote import SshRemote
from py2030.utils.shell_script import ShellScript

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
        self.vids_path = self.path + '/bin/data/vids'
        self.images_path = self.path + '/bin/data/images'

from scp import SCPClient
import sys, time, subprocess

class Tool:
    def __init__(self):
        self.config_file = self._get_config_file()
        self.remotes = self._get_remotes()
        self.sshs = {}

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

    def connect(self):
        for remote in self.remotes:
            ssh = self.get_ssh_for_remote(remote)
            if ssh:
                self.sshs[remote] = ssh

    def disconnect(self):
        for ssh in self.sshs.values():
            ssh.disconnect()
        self.sshs = {}

    def get_ssh_for_remote(self, remote, connect=True):
        ssh = self.sshs[remote] if remote in self.sshs else None

        # found existing connection
        if ssh:
            return ssh

        # should we even attempt to connect?
        if not connect:
            return None

        # try to create a connection
        ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
        if ssh.connect():
            return ssh

        # failed to connect
        return None

    def get_connections(self, connect=True, builders_only=False, non_builders_only=False):
        connects = []
        for remote in self.remotes:
            if builders_only and not remote.ofbuilder:
                continue
            if non_builders_only and remote.ofbuilder:
                continue

            ssh = self.get_ssh_for_remote(remote, connect)
            if ssh:
                connects.append({'remote': remote, 'ssh': ssh})

        return connects


    def get_py(self):
        tarfile='py2030.tar.gz'
        print 'TODO: implement get_py'

    def push_py(self, remote, ssh):
        tarfile='py2030.tar.gz'
        folder='py2030-'+time.strftime('%Y%m%d_%H%M%S')
        installcmd = ShellScript('data/scripts/py2030_tar_install.sh').get_script({'tarfile': tarfile, 'folder': folder})

        # push package
        ssh.put(tarfile, tarfile)
        # install package
        ssh.cmd(installcmd)
        # remove package
        ssh.cmd('rm '+tarfile)

    # local of2030

    # def get_of_local(self):
    #     tarfile = 'of2030.tar.gz'
    #     folder = Of2030(config_file=self.config_file).path
    #     ShellScript('data/scripts/of2030_tar_create.sh').execute({'tarfile': tarfile, 'folder': folder})


    def get_src(self):
        tarfile = 'of2030-src.tar.gz'
        folder = Of2030(config_file=self.config_file).path
        ShellScript('data/scripts/of2030src_tar_create.sh').execute({'tarfile': tarfile, 'folder': folder})

    def push_src(self, remote, ssh):
        tarfile='of2030-src.tar.gz'
        offolder=remote.of2030.path
        cmd = ShellScript('data/scripts/of2030src_tar_install.sh').get_script({'tarfile': tarfile, 'offolder': offolder})

        # push package
        ssh.put(tarfile, tarfile)
        # install package
        ssh.cmd(cmd)
        # remove package
        ssh.cmd('rm '+tarfile)


    def get_xml(self):
        tarfile = 'of2030-xml.tar.gz'
        folder = Of2030(config_file=self.config_file).path
        ShellScript('data/scripts/of2030xml_tar_create.sh').execute({'tarfile': tarfile, 'folder': folder})

    def push_xml(self, remote, ssh):
        tarfile = 'of2030-xml.tar.gz'
        offolder=remote.of2030.path
        cmd = ShellScript('data/scripts/of2030xml_tar_install.sh').get_script({'tarfile': tarfile, 'offolder': offolder, 'client_id': remote.name})

        # push package
        ssh.put(tarfile, tarfile)
        # install package
        ssh.cmd(cmd)
        # remove package
        ssh.cmd('rm '+tarfile)

    # raspi of2030 build

    def get_build(self, remote, ssh):
        # remote = self._get_of_builder_remote()

        # if not remote:
        #     print 'could not find ofbuilder-enabled remote'
        #     return False

        # ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
        # if not ssh.connect():
        #     # abort
        #     return False

        tarfile = 'of2030.tar.gz'
        # package bin folder into tar.gz file
        ssh.cmd(ShellScript('data/scripts/of2030_tar_create.sh').get_script({'tarfile': tarfile, 'folder': remote.ofpath}))
        # fetch package
        ssh.get(tarfile)
        # remove remotely
        ssh.cmd('rm '+tarfile)

    def push_build(self, remote, ssh): #skip_builders=True, builders_only=False):
        # for remote in self.remotes:
        #     if remote.ofbuilder and skip_builders:
        #         # skip builder
        #         continue

        #     if builders_only and not remote.ofbuilder:
        #         # skip non-builder
        #         continue

        #     ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
        #     if not ssh.connect():
        #         # could not connect to current remote, move to next one
        #         continue

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

    def get_bin(self, remote, ssh):
        tarfile = 'of2030-bin.tar.gz'

        # remote = self._get_of_builder_remote()

        # if not remote:
        #     print 'could not find ofbuilder-enabled remote'
        #     return False

        # ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
        # if not ssh.connect():
        #     # abort
        #     return False

        # package bin folder into tar.gz file
        ssh.cmd(ShellScript('data/scripts/of2030bin_tar_create.sh').get_script({'tarfile': tarfile, 'offolder': remote.ofpath}))
        # fetch package
        ssh.get(tarfile)
        # remove remotely
        ssh.cmd('rm '+tarfile)

    def push_bin(self, remote, ssh): #skipBuilders=True):
        # for remote in self.remotes:
        #     if remote.ofbuilder and skipBuilders:
        #         # skip builder
        #         continue

        #     # if builders_only and not remote.ofbuilder:
        #     #     # skip non-builder
        #     #     continue

        #     ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
        #     if not ssh.connect():
        #         # could not connect to current remote, move to next one
        #         continue

        tarfile = 'of2030-bin.tar.gz'
        ss = ShellScript('data/scripts/of2030bin_tar_install.sh')
        installcmd = ss.get_script({'tarfile': tarfile, 'offolder': remote.ofpath})

        # push package
        ssh.put(tarfile, tarfile)
        # install package
        ssh.cmd(installcmd)
        # remove package
        ssh.cmd('rm '+tarfile)

    # # control remote processes
    # def start(self, remote, ssh):
    #     # for remote in self.remotes:
    #     #     ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
    #     #     if not ssh.connect():
    #     #         # could not connect to current remote, move to next one
    #     #         continue
    #
    #     cmd = ShellScript('data/scripts/rpi_start.sh').get_script()
    #     # restart processes
    #     ssh.cmd(cmd, wait=False)
    #
    # def stop(self, remote, ssh):
    #     # for remote in self.remotes:
    #     #     ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
    #     #     if not ssh.connect():
    #     #         # could not connect to current remote, move to next one
    #     #         continue
    #     cmd = ShellScript('data/scripts/rpi_stop.sh').get_script()
    #     # restart processes
    #     ssh.cmd(cmd, wait=False)
    #
    # def restart(self, remote, ssh):
    #     # for remote in self.remotes:
    #     #     ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
    #     #     if not ssh.connect():
    #     #         # could not connect to current remote, move to next one
    #     #         continue
    #     startcmd = ShellScript('data/scripts/rpi_start.sh').get_script()
    #     stopcmd = ShellScript('data/scripts/rpi_stop.sh').get_script()
    #     # restart processes
    #     ssh.cmd(startcmd, wait=False)
    #     ssh.cmd(stopcmd, wait=False)

    # shaders

    def get_shaders(self, folder=None):
        if not folder:
            folder = Of2030(self.config_file).raspi_shaders_folder_path

        tarfile = 'shadersES2.tar.gz'
        ShellScript('data/scripts/shaders_tar_create.sh').execute({'tarfile': tarfile, 'folder': folder})

    def push_shaders(self, remote, ssh):
        # for remote in self.remotes:
        #     if remote.ofbuilder and skip_builders:
        #         continue

        #     ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
        #     if not ssh.connect():
        #         # could not connect to current remote, move to next one
        #         continue

        tarfile='shadersES2.tar.gz'
        location=remote.ofshadersfolder()
        # push package
        ssh.put(tarfile, tarfile)
        # install package
        ssh.cmd(ShellScript('data/scripts/shaders_tar_install.sh').get_script({'tarfile': tarfile, 'location': location}))
        # remove package
        ssh.cmd('rm '+tarfile)


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

    def push_osc(self, remote, ssh):
        # for remote in self.remotes:
        #     ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
        #     if not ssh.connect():
        #         # could not connect to current remote, move to next one
        #         continue

        tarfile='osc.tar.gz'
        location=remote.of2030.osc_path

        # push package
        ssh.put(tarfile, tarfile)
        # install package
        ssh.cmd(ShellScript('data/scripts/osc_tar_install.sh').get_script({'tarfile': tarfile, 'location': location}))
        # remove package
        ssh.cmd('rm '+tarfile)

    def get_img(self, folder=None):
        # foler not specified by caller?
        if not folder:
            # try to get osc_folder setting from config file
            folder = self.config_file.get_value('py2030.images_folder', None)
        # folder not specified in config file?
        if not folder:
            # use default osc folder of local of2030 folder
            folder = Of2030(self.config_file).images_path

        tarfile = 'imgs.tar.gz'
        ShellScript('data/scripts/images_tar_create.sh').execute({'tarfile': tarfile, 'folder': folder})

    def push_img(self, remote, ssh, put=True, install=True):
        # for remote in self.remotes:
        #     ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
        #     if not ssh.connect():
        #         # could not connect to current remote, move to next one
        #         continue

        tarfile='imgs.tar.gz'
        location=remote.of2030.images_path

        if put:
            # push package
            ssh.put(tarfile, tarfile)

        if install:
            # install package
            ssh.cmd(ShellScript('data/scripts/images_tar_install.sh').get_script({'tarfile': tarfile, 'location': location}))
            # remove package
            ssh.cmd('rm '+tarfile)


    def get_vids(self, folder=None):
        # foler not specified by caller?
        if not folder:
            # try to get osc_folder setting from config file
            folder = self.config_file.get_value('py2030.vids_folder', None)
        # folder not specified in config file?
        if not folder:
            # use default osc folder of local of2030 folder
            folder = Of2030(self.config_file).vids_path

        tarfile = 'vids.tar.gz'
        ShellScript('data/scripts/vids_tar_create.sh').execute({'tarfile': tarfile, 'folder': folder})

    def push_vids(self, remote, ssh, put=True, install=True):
        # for remote in self.remotes:
        #     ssh = SshRemote(ip=remote.ip, hostname=remote.hostname, username=remote.ssh_username, password=remote.ssh_password)
        #     if not ssh.connect():
        #         # could not connect to current remote, move to next one
        #         continue

        tarfile='vids.tar.gz'
        location=remote.of2030.vids_path

        if put:
            # push package
            ssh.put(tarfile, tarfile)

        if install:
            # install package
            ssh.cmd(ShellScript('data/scripts/vids_tar_install.sh').get_script({'tarfile': tarfile, 'location': location}))
            # remove package
            ssh.cmd('rm '+tarfile)

    # run generic command(s) on all remotes

    def execute_argv(self, argv):
        # local stuff to prepare before going to the remote connections
        if '--get-xml' in argv or '--update-xml' in argv:
            self.get_xml()

        if '--get-src' in argv or '--update-src' in argv:
            self.get_src()

        if '--get-bin' in argv or '--update-bin' in argv:
            cons = self.get_connections(builders_only=True)
            if len(cons) > 0:
                self.get_bin(cons[0]['remote'], cons[0]['ssh'])
            else:
                print 'could not get ofbuilder connection to do --get-bin'

        if '--get-osc' in argv or '--update-osc' in argv:
            self.get_osc()

        if '--get-vids' in argv or '--update-vids' in argv:
            self.get_vids()
        if '--get-img' in argv or '--update-img' in argv:
            self.get_img()

        if '--get-shaders' in argv or '--update-shaders' in argv:
            self.get_shaders()

        if '--get-py' in argv or '--update-py' in argv:
            tarfile='py2030.tar.gz'
            ShellScript('data/scripts/py2030_tar_create.sh').execute({'tarfile': tarfile})

        # each connection
        cons = self.get_connections()
        for con in cons:
            remote = con['remote']
            ssh = con['ssh']

            if '--push-xml' in argv or '--update-xml' in argv:
                self.push_xml(remote, ssh)

            if remote.ofbuilder:
                if '--push-src' in argv or '--update-src' in argv:
                    self.push_src(remote, ssh)
                if '--build' in argv or '--build-of' in argv:
                    ssh.cmd('make Debug -C of2030 > buildlog.txt &')

            if not remote.ofbuilder:
                if '--push-bin' in argv or '--update-bin' in argv:
                    self.push_bin(remote, ssh)

            if '--push-osc' in argv or '--update-osc' in argv:
                self.push_osc(remote, ssh)

            if '--push-img' in argv or '--update-img' in argv:
                self.push_img(remote, ssh)

            if '--put-img' in argv:
                self.push_img(remote, ssh, put=True, install=False)

            if '--install-img' in argv:
                self.push_img(remote, ssh, put=False, install=True)

            if '--push-shaders' in argv or '--update-shaders' in argv:
                self.push_shaders(remote, ssh)

            if '--push-vids' in argv or '--update-vids' in argv:
                self.push_vids(remote, ssh)

            if '--put-vids' in argv:
                self.push_vids(remote, ssh, put=True, install=False)

            if '--install-vids' in argv:
                self.push_vids(remote, ssh, put=False, install=True)

            if not remote.ofbuilder:
                if '--stop' in argv or '--stop-of' in argv or '--restart' in argv or '--restart-of' in argv:
                    ssh.cmd("sudo killall of2030\n\n", wait=False)
                    time.sleep(0.5)
                    ssh.cmd("sudo killall of2030\n\n", wait=False)
                    time.sleep(1.0)

                if '--start' in argv or '--start-of' in argv or '--restart' in argv or '--restart-of' in argv:
                    ssh.cmd('make RunRelease -C of2030 &\n\n', wait=False)
                    time.sleep(1.0)

            if '--reboot' in argv:
                ssh.cmd('sudo reboot')

            if '--shutdown' in argv:
                ssh.cmd('sudo shutdown -h now')

            if '--push-py' in argv or '--update-py' in argv:
                self.push_py(remote, ssh)


        # post remote cleanups

        local_files_to_remove = []

        if '--update-xml' in argv:
            local_files_to_remove.append('of2030-xml.tar.gz')

        if '--update-src' in argv:
            local_files_to_remove.append('of2030-src.tar.gz')

        if '--update-bin' in argv:
            local_files_to_remove.append('of2030-bin.tar.gz')

        if '--update-osc' in argv:
            local_files_to_remove.append('osc.tar.gz')

        if '--update-vids' in argv:
            local_files_to_remove.append('vids.tar.gz')

        if '--update-img' in argv:
            local_files_to_remove.append('imgs.tar.gz')

        if '--update-shaders' in argv:
            local_files_to_remove.append('shadersES2.tar.gz')

        for f in local_files_to_remove:
            print 'removing local copy of:', f
            subprocess.call(['rm', f])

        # parser.add_option('--start-of', dest='start_of', action="store_true", default=False)
        # parser.add_option('--stop-of', dest='stop_of', action="store_true", default=False)
        # parser.add_option('--restart-of', dest='restart_of', action="store_true", default=False)

        # parser.add_option('--stop', dest='stop', action="store_true", default=False)
        # parser.add_option('--start', dest='start', action="store_true", default=False)
        # parser.add_option('--restart', dest='restart', action="store_true", default=False)

        # parser.add_option('--shutdown', dest='shutdown', action="store_true", default=False)
        # parser.add_option('--reboot', dest='reboot', action="store_true", default=False)

        # parser.add_option('--get-of', dest='get_of', action="store_true", default=False)
        # parser.add_option('--push-of', dest='push_of', action="store_true", default=False)
        # parser.add_option('--update-of', dest='update_of', action="store_true", default=False)

        # parser.add_option('--get-local-of', dest='get_local_of', action="store_true", default=False)
        # parser.add_option('--push-local-of', dest='push_local_of', action="store_true", default=False)
        # parser.add_option('--update-local-of', dest='update_local_of', action="store_true", default=False)

        # parser.add_option('--get-py', dest='get_py', action="store_true", default=False)
        # parser.add_option('--push-py', dest='push_py', action="store_true", default=False)
        # parser.add_option('--update-py', dest='update_py', action="store_true", default=False)

        # # params
        # parser.add_option('-f', '--folder', dest='folder', default=None)


    # # of2030
    #
    # if opts.update_of:
    #     tool.fetch_of_build()
    #     tool.push_of_build(skip_builders=True, builders_only=False)
    #     tarfile='of2030.tar.gz'
    #     print 'DONE, removing local copy;', tarfile
    #     subprocess.call(['rm', tarfile])
    #
    # if opts.get_of:
    #     tool.fetch_of_build()
    #
    # if opts.push_of:
    #     tool.push_of_build(skip_builders=True, builders_only=False)
    #
    # if opts.get_local_of:
    #     tool.get_local_of_tar()
    #
    # if opts.push_local_of:
    #     tool.push_of_build(skip_builders=False, builders_only=True)
    #
    # if opts.update_local_of:
    #     tool.get_local_of_tar()
    #     tool.push_of_build(skip_builders=False, builders_only=True)
    #     tarfile='of2030.tar.gz'
    #     print 'DONE, removing local copy;', tarfile
    #     subprocess.call(['rm', tarfile])
    #
    #
    # if opts.get_ofbin:
    #     tool.get_ofbin_tar()
    #
    # if opts.push_ofbin:
    #     tool.push_ofbin_tar()
    #
    # if opts.update_ofbin:
    #     tool.get_ofbin_tar()
    #     tool.push_ofbin_tar()
    #     tarfile = 'of2030-bin.tar.gz'
    #     print 'DONE, removing local copy;', tarfile
    #     subprocess.call(['rm', tarfile])
    #
    # # of2030/bin/data/osc (presets)
    #
    # if opts.get_osc:
    #     tool.get_osc(opts.folder)
    #
    # if opts.push_osc:
    #     tool.push_osc()
    #
    # if opts.update_osc:
    #     tool.get_osc(opts.folder)
    #     tool.push_osc()
    #     tarfile = 'osc.tar.gz'
    #     print 'DONE, removing local copy;', tarfile
    #     subprocess.call(['rm', tarfile])
    #
    # if opts.get_vids:
    #     tool.get_vids(opts.folder)
    #
    # if opts.push_vids:
    #     tool.push_vids(push=True, install=False)
    #
    # if opts.install_vids:
    #     tool.push_vids(push=False, install=True)
    #
    # if opts.update_vids:
    #     tool.get_vids(opts.folder)
    #     tool.push_vids(push=True, install=True)
    #     tarfile = 'vids.tar.gz'
    #     print 'DONE, removing local copy;', tarfile
    #     subprocess.call(['rm', tarfile])
    #
    # # of2030/bin/data/shadersES2
    #
    # if opts.get_shaders:
    #     tool.get_shaders(opts.folder)
    #
    # if opts.push_shaders:
    #     tool.push_shaders()
    #
    # if opts.update_shaders:
    #     tool.get_shaders(opts.folder)
    #     tool.push_shaders()
    #     tarfile = 'shadersES2.tar.gz'
    #     print 'DONE, removing local copy;', tarfile
    #     subprocess.call(['rm', tarfile])
    #
    # # py2030
    # if opts.get_py:
    #     # create_py_tar
    #     tarfile='py2030.tar.gz'
    #     ShellScript('data/scripts/py2030_tar_create.sh').execute({'tarfile': tarfile})
    #
    # if opts.push_py:
    #     tool.push_py()
    #
    # if opts.update_py:
    #     # create_py_tar
    #     tarfile='py2030.tar.gz'
    #     ShellScript('data/scripts/py2030_tar_create.sh').execute({'tarfile': tarfile})
    #
    #     tool.push_py()
    #
    #     tarfile='py2030.tar.gz'
    #     print 'DONE, removing local copy;', tarfile
    #     subprocess.call(['rm', tarfile])
    #
    # # rpi of2030 and py2030 control
    #
    # if opts.stop:
    #     tool.stop()
    # if opts.start:
    #     tool.start()
    #
    # if opts.restart:
    #     tool.restart()
    #
    # if opts.start_of:
    #     # tool.cmd_all_remotes('./startof.sh\n\n', wait=False, skip_builders=True, sleep=1.0)
    #     tool.cmd_all_remotes('make RunDebug -C of2030 &\n\n', wait=False, skip_builders=True, sleep=1.0)
    # if opts.stop_of:
    #     tool.cmd_all_remotes('sudo killall of2030_debug\n\n', wait=False, skip_builders=True, sleep=1.0)
    # if opts.restart_of:
    #     tool.cmd_all_remotes('sudo killall of2030_debug\n\nmake RunDebug -C of2030 &\n\n', wait=False, skip_builders=True, sleep=1.0)
    #
    # # rpi system
    #
    # if opts.reboot:
    #     tool.cmd_all_remotes('sudo reboot')
    #
    # if opts.shutdown:
    #     tool.cmd_all_remotes('sudo shutdown -h now')


try:
    import OSC
except ImportError:
    print "importing embedded version of pyOSC library for py2030.outputs.osc"
    import py2030.dependencies.OSC as OSC

class Client:
    def __init__(self, osc_port=2130, osc_host='127.0.0.1', verbose=True):
        self.osc_port = osc_port
        self.osc_host = osc_host
        self.verbose = verbose

        # attributes
        self.client = None
        self.connected = False
        self.running = False

    def __del__(self):
        self.stop()

    def start(self):
        if self._connect():
            self.running = True

    def stop(self):
        if self.connected:
            self._disconnect()
        self.running = False

    def _connect(self):
        try:
            self.client = OSC.OSCClient()
            self.client.connect((self.osc_host, self.osc_port))
        except OSC.OSCClientError as err:
            ColorTerminal().fail("OSC connection failure: {0}".format(err))
            return False

        self.connected = True
        print "OSC client connected to {0}:{1}".format(self.osc_host, str(self.osc_port))
        return True

    def _disconnect(self):
        if not hasattr(self, 'client') or not self.client:
            return False
        self.client.close()
        self.client = None
        self.connected = False
        print "OSC client closed"
        return True

    def send(self, addr, data=[]):
        if not self.connected:
            print 'client not connect, not sending message ', addr, data
            return

        msg = OSC.OSCMessage()
        msg.setAddress(addr) # set OSC address

        for item in data:
            msg.append(item)

        try:
            self.client.send(msg)
        except OSC.OSCClientError as err:
            pass
        except AttributeError as err:
            print '[Tool.Client {0}:{1}] error:'.format(self.osc_host, self.osc_port)
            print err
            self.stop()

        if self.verbose:
            print '[Tool.Client {0}:{1}]:'.format(self.osc_host, self.osc_port), addr, data

class Service:
    def __init__(self, osc_port=2130, verbose=True):
        self.osc_port = osc_port
        self.verbose = verbose

        self.running=False
        self.connected=False
        self.osc_server=None
        self.got_pong = False
        self.tool = None

    def __del__(self):
        self.stop()

    def start(self):
        if self._connect():
            self.running = True

    def stop(self):
        if self.connected:
            self._disconnect()
        if self.tool:
            self.tool.disconnect()
            self.tool = None
        self.running = False

    def update(self):
        if not self.connected:
            return

        # we'll enforce a limit to the number of osc requests
        # we'll handle in a single iteration, otherwise we might
        # get stuck in processing an endless stream of data
        limit = 50
        count = 0

        # clear timed_out flag
        self.osc_server.timed_out = False

        # handle all pending requests then return
        while not self.osc_server.timed_out and count < limit:
            try:
                self.osc_server.handle_request()
                count += 1
            except Exception as exc:
                print 'Something went wrong while handling incoming OSC messages:'
                print exc

    def _connect(self):
        if self.connected:
            print 'Tool.Service - Already connected'
            return False

        try:
            self.osc_server = OSC.OSCServer(('', self.osc_port))
        except Exception as err:
            # something went wrong, cleanup
            self.connected = False
            self.osc_server = None
            print "{0}\nOSC Server could not start @ {1}".format(err, str(self.osc_port))
            # abort
            return False

        # register time out callback
        self.osc_server.handle_timeout = self._onTimeout
        self.osc_server.addMsgHandler('default', self._onMessage)
        self.connected = True
        print "OSC Server running @ {0}".format(str(self.osc_port))
        return True

    def _disconnect(self):
        if hasattr(self, 'osc_server') and self.osc_server:
            self.osc_server.close()
            self.connected = False
            self.osc_server = None
            print 'OSC Server stopped'

    def _onTimeout(self):
        self.osc_server.timed_out = True

    def _onMessage(self, addr, tags, data, client_address):
        if self.verbose:
            print 'Tool.Service got OSC Message {0}'.format((addr, tags, data, client_address))

        # respond to pings with pong
        if addr == '/ping':
            cport = data[0] if len(data) > 0 else 2132
            c = Client(osc_host=client_address[0], osc_port=cport)
            c.start()
            c.send('/pong')
            return

        # set got pong when receiving a /pong message
        if addr == '/pong':
            self.got_pong = True
            return

        if addr == '/argv':
            if not self.tool:
                self.tool = Tool()
                # self.tool.connect()
            self.tool.execute_argv(data)

def main(opts, args):
    if opts.service:
        # the service does the actual execution
        service = Service()
        service.start()

        try:
            while True:
                service.update()
        except KeyboardInterrupt:
            print ' KeyboardInterrupt; quitting'
        service.stop()
        return


    # the service receives '/pong' messages
    service = Service(osc_port=2132)
    service.start()

    # the client sends operation command to the service via OSC
    # the service can run in a separate process (keeping SSH connections alive)
    # or simply be part of this process
    client = Client()
    client.start()

    # check if there's a service running
    remote_service_running = False

    client.send('/ping', [service.osc_port])
    t = time.time()
    while time.time() - t < 2.0:
        service.update()
        if service.got_pong:
            remote_service_running = True
            # break out of the while loop
            break

    # stop local service (only used to receive /pong from remote service)
    service.stop()
    service=None

    if remote_service_running:
        # our client is already connected to the remote service
        print 'using remote service at {0}'.format(client.osc_port)
        client.send('/argv', sys.argv)
        client.stop()
        client = None
        return

    # no remote service detected, run locally
    client.stop()
    client = None

    #client = Client(osc_port=2032)
    #print 'using local service at {0}'.format(client.osc_port)
    tool = Tool()
    Tool().execute_argv(sys.argv)

    # done
    return

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()

    # actions
    parser.add_option('-s', '--service', dest='service', action="store_true", default=False)
    parser.add_option('--shutdown', dest='shutdown', action="store_true", default=False)
    parser.add_option('--reboot', dest='reboot', action="store_true", default=False)
    
    parser.add_option('--stop', dest='stop', action="store_true", default=False)
    parser.add_option('--start', dest='start', action="store_true", default=False)
    parser.add_option('--restart', dest='restart', action="store_true", default=False)
    parser.add_option('--start-of', dest='start_of', action="store_true", default=False)
    parser.add_option('--stop-of', dest='stop_of', action="store_true", default=False)
    parser.add_option('--restart-of', dest='restart_of', action="store_true", default=False)
    parser.add_option('--build', dest='build_of', action="store_true", default=False)
    # parser.add_option('--get-of', dest='get_of', action="store_true", default=False)
    # parser.add_option('--push-of', dest='push_of', action="store_true", default=False)
    # parser.add_option('--update-of', dest='update_of', action="store_true", default=False)

    # parser.add_option('--get-local-of', dest='get_local_of', action="store_true", default=False)
    # parser.add_option('--push-local-of', dest='push_local_of', action="store_true", default=False)
    # parser.add_option('--update-local-of', dest='update_local_of', action="store_true", default=False)
    
    parser.add_option('--get-xml', dest='get_ofxml', action="store_true", default=False)
    parser.add_option('--push-xml', dest='push_ofxml', action="store_true", default=False)
    parser.add_option('--update-xml', dest='update_ofxml', action="store_true", default=False)
    
    parser.add_option('--get-src', dest='get_ofsrc', action="store_true", default=False)
    parser.add_option('--push-src', dest='push_ofsrc', action="store_true", default=False)
    parser.add_option('--update-src', dest='update_ofsrc', action="store_true", default=False)

    parser.add_option('--get-bin', dest='get_ofbin', action="store_true", default=False)
    parser.add_option('--push-bin', dest='push_ofbin', action="store_true", default=False)
    parser.add_option('--update-bin', dest='update_ofbin', action="store_true", default=False)

    parser.add_option('--get-shaders', dest='get_shaders', action="store_true", default=False)
    parser.add_option('--push-shaders', dest='push_shaders', action="store_true", default=False)
    parser.add_option('--update-shaders', dest='update_shaders', action="store_true", default=False)

    parser.add_option('--get-osc', dest='get_osc', action="store_true", default=False)
    parser.add_option('--push-osc', dest='push_osc', action="store_true", default=False)
    parser.add_option('--update-osc', dest='update_osc', action="store_true", default=False)

    parser.add_option('--get-vids', dest='get_vids', action="store_true", default=False)
    parser.add_option('--push-vids', dest='push_vids', action="store_true", default=False)
    parser.add_option('--put-vids', dest='push_vids', action="store_true", default=False)
    parser.add_option('--install-vids', dest='install_vids', action="store_true", default=False)
    parser.add_option('--update-vids', dest='update_vids', action="store_true", default=False)

    parser.add_option('--get-img', dest='get_img', action="store_true", default=False)
    parser.add_option('--push-img', dest='push_img', action="store_true", default=False)
    parser.add_option('--put-img', dest='push_img', action="store_true", default=False)
    parser.add_option('--install-img', dest='install_img', action="store_true", default=False)
    parser.add_option('--update-img', dest='update_img', action="store_true", default=False)

    parser.add_option('--get-py', dest='get_py', action="store_true", default=False)
    parser.add_option('--push-py', dest='push_py', action="store_true", default=False)
    parser.add_option('--update-py', dest='update_py', action="store_true", default=False)

    # params
    
    parser.add_option('-c', '--client', dest='client', action="store_true", default=False)
    parser.add_option('-f', '--folder', dest='folder', default=None)
    # parser.add_option('-f', '--file', dest='file', default=None)
    parser.add_option('-l', '--loop', dest='loop', action="store_true", default=False)
    parser.add_option('-t', '--threaded', dest='threaded', action="store_true", default=False)
    parser.add_option('--install', dest='install', action="store_true", default=False)
    parser.add_option('--bootstrap', dest='bootstrap', action="store_true", default=False)
    parser.add_option('--route-ip', dest="route_ip", action="store_true", help="Route IP address (default: the controller profile's osc_out_ip value from the config file) to specific interface (default: en0)", default=None)
    options, args = parser.parse_args()
    del OptionParser
    main(options, args)
