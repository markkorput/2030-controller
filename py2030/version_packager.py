import os

class VersionPackager:
    def __init__(self, options = {}):
        self.src = options['source'] if 'source' in options else 'py2030'
        self.dest = options['destination'] if 'destination' in options else 'data/py2030-{version}.tar.gz'
        self.version = options['version'] if 'version' in options else '0.0.0'
        self.dest_path = self.dest.replace('{version}', self.version)

    def package_exists(self):
        return os.path.isfile(self.dest_path)

    def package(self, repackage=False):
        if self.package_exists() and not repackage:
            return

        command = 'tar -czf ' + self.dest_path + ' ' + self.src
        print '[VersionPackager] running command', command
        os.system(command)
