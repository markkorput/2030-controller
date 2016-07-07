from py2030.interface import Interface
import os

class HohVidStarter:
  def __init__(self, options = {}):
    # params
    self.options = options
    # config
    self.interface = self.options['interface'] if 'interface' in self.options else Interface.instance()
    self.verbose = 'verbose' in self.options and self.options['verbose']

  def setup(self):
    # get video paths
    data = self.options['vids'] if 'vids' in self.options else {}
    self.startVidPath = data['start'] if 'start' in data else ''
    self.winPaths = []
    p = data['win1'] if 'win1' in data else ''
    self.winPaths.append(p)
    p = data['win2'] if 'win2' in data else ''
    self.winPaths.append(p)
    p = data['win3'] if 'win3' in data else ''
    self.winPaths.append(p)

    # register callbacks
    print 'registering hoh video starter callbacks'
    self.interface.hohStartEvent += self._onStart
    self.interface.hohStopEvent += self._onStop
    self.interface.hohWinnerEvent += self._onWinner

  def _onStart(self):
    cmd = 'omxplayer ' + self.startVidPath + ' &'
    if self.verbose:
        print 'starting video with command:', cmd
    os.system(cmd)

  def _onStop(self):
    cmd = 'pkill omxplayer'
    if self.verbose:
        print 'killing video with command:', cmd
    os.system(cmd)

  def _onWinner(self, winner):
    if winner < 1 or winner > len(self.winPaths):
        print 'invalid winner value:', winner
        return

    cmd = 'omxplayer ' + self.winPaths[winner-1] + ' &'
    if self.verbose:
        print 'starting video with command:', cmd
    os.system(cmd)
