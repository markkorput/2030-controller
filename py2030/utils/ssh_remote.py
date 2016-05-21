import paramiko, os, re, time, subprocess, socket
from scp import SCPClient
from py2030.utils.color_terminal import ColorTerminal

class SshRemote:
    def __init__(self, ip=None, username=None, password=None, hostname=None):
        self.ip = ip
        self.username = username
        self.password = password
        self.hostname = hostname

        self.connected = False
        self.client = None

        # these will hold exec command results
        self.stdin = None
        self.stdout = None
        self.stderr = None

        if self.ip == None and self.hostname:
            try:
                self.ip  = socket.gethostbyname(self.hostname)
            except socket.gaierror as err:
                try:
                    self.ip  = socket.gethostbyname(self.hostname+'.local')
                except socket.gaierror as err:
                    print 'could not get ip from hostname'
                    print err
                    return

    def __del__(self):
        self.destroy()

    def destroy(self):
        if self.connected:
            self.disconnect()

    def connect(self):
        if not self.ip:
            print "no ip for hostname ({0}), can't connect".format(self.hostname)
            return False

        # if self.connected:
        #     return None
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.client.connect(self.ip, username=self.username, password=self.password)
        except paramiko.ssh_exception.AuthenticationException as err:
            ColorTerminal().fail('[SshRemote] ssh authentication failed on host {0} ({1})'.format(self.ip, self.hostname))
            self.connected = False
            return False

        print 'ssh connection established with', self.ip, self.hostname
        self.connected = True
        return True

    def disconnect(self):
        if self.client:
            self.client.close()
            print 'ssh connection closed'
            self.client = None

    def cmd(self, command, wait=True):
        print "ssh-cmd:\n", command
        self.stdin, self.stdout, self.stderr = self.client.exec_command(command)
        if wait:
            for line in self.stdout:
                pass
            for line in self.stderr:
                try:
                    print '[STDERR]',str(line.strip('\n'))
                except UnicodeEncodeError as err:
                    print '[STDERR] (unicode issue with printing error);'
                    print err

    def put(self, local_file_path, remote_file_name):
        print "ssh-put:", local_file_path, remote_file_name
        with SCPClient(self.client.get_transport()) as scp:
            scp.put(local_file_path, remote_file_name)

    def get(self, remote_file_name):
        print "ssh-get:", remote_file_name
        with SCPClient(self.client.get_transport()) as scp:
            scp.get(remote_file_name)
