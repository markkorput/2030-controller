import os, logging, re, subprocess

class ShellScript:
    def __init__(self, script_path, remove_comments=True):
        self.script_path = script_path
        self.remove_comments = remove_comments
        self.file = None
        self.last_line = None

    def next_line(self):
        if not self.file:
            try:
                self.file = open(self.script_path)
            except IOError:

                logging.getLogger().error('ShellScript could not open file:', self.script_path)
                self.file=None
                return None

        while True:
            line = self.file.readline()

            # end-of-file?
            if line == '':
                self.file.close()
                self.file = None
                return None

            # comment?
            if self.remove_comments and re.match(r'\s*#', line):
                # try next line
                continue

            self.last_line = line.strip()
            return self.last_line

        # this is never reached..
        return None

    def get_script(self):
        exe_lines = []
        while self.next_line():
            exe_lines.append(self.last_line)
        return "\n".join(exe_lines)

    def execute(self):
        script = self.get_script()
        print "executing script:", script
        os.system(script)

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-f', '--file', dest='file', default="data/scripts/py2030_tar_create.sh")
    options, args = parser.parse_args()
    # logging.getLogger('ShellScript').setLevel(logging.INFO)
    # logging.getLogger().warning('executing: ', options.file)
    ShellScript(options.file).execute()
    # logging.getLogger().warning('done')
