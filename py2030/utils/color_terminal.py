class ColorTerminal(object):
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def __init__(self):
        pass

    def output(self, msg, prefix=None):
        if prefix:
            msg = prefix + msg + ColorTerminal.ENDC
        print(msg)

    def red(self, msg): self.output(msg, ColorTerminal.RED)
    def yellow(self, msg): self.output(msg, ColorTerminal.YELLOW)
    def blue(self, msg): self.output(msg, ColorTerminal.BLUE)
    def green(self, msg): self.output(msg, ColorTerminal.GREEN)
    def bold(self, msg): self.output(msg, ColorTerminal.BOLD)
    def underline(self, msg): self.output(msg, ColorTerminal.UNDERLINE)
    def header(self, msg): self.output(msg, ColorTerminal.HEADER)

    def warn(self, msg): self.yellow(msg)
    def fail(self, msg): self.red(msg)
    def success(self, msg): self.output(msg, ColorTerminal.GREEN)
