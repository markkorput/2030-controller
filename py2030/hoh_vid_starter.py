from py2030.interface import Interface
try:
    from omxplayer import OMXPlayer
except:
    print '[HohVidStarter] no omxplayer'
    OMXPlayer = None

class HohVidStarter:
  def __init__(self, options = {}):
    # params
    self.options = options
    # config
    self.interface = self.options['interface'] if 'interface' in self.options else Interface.instance()
    self.verbose = 'verbose' in self.options and self.options['verbose']
    self.player = None

  def __del__(self):
      if self.player:
          self.unload()

  def setup(self):
    # get video paths
    self.vidPaths = []
    self.vidPaths = self.options['vids'] if 'vids' in self.options else []
    print '[HohVidStarter] video paths:', self.vidPaths
    # register callbacks
    print 'registering hoh video starter callbacks'
    self.interface.hohStartEvent += self._onStart
    self.interface.hohLoadEvent += self._onLoad
    self.interface.hohPlayEvent += self._onPlay
    self.interface.hohStopEvent += self._onStop

  def unload(self):
    if self.player:
      self.player.quit()
      self.player = None

  def load(self, videoPath):
    if self.verbose:
      print '[HohVidStarter#start] loading player with:', videoPath

    # close existing video
    if self.player:
      self.unload()

    # this will be paused by default
    if OMXPlayer:
        # start omx player without osd and sending audio through analog jack
        self.player = OMXPlayer(videoPath, args=['--no-osd', '--adev', 'local'])

  def start(self):
    if not self.player:
      print '[HohVidStarter#start] No video loaded'
      return
    if self.verbose:
      print '[HohVidStarter#start] self.player.play()'
    self.player.play()

  def pause(self):
    if not self.player:
      print '[HohVidStarter#pause] No video loaded'
      return
    if self.verbose:
      print '[HohVidStarter#start] self.player.pause()'

    self.player.pause()

  def stop(self):
    if not self.player:
      print '[HohVidStarter#pause] No video loaded'
      return
    if self.verbose:
      print '[HohVidStarter#start] self.player.stop()'

    self.player.stop()

  #
  # Callback methods
  #

  def _onStart(self, no):
    try:
      no = int(no)
    except:
      no = 0

    if no < 0 or no >= len(self.vidPaths):
      print '[HohVidStarter] invalid start value:', no
      return

    vidPath = self.vidPaths[no]
    if vidPath == '':
        print '[HohVidStarter] empty video path, not starting anything'
        return

    # cmd = 'omxplayer ' + self.vidPaths[0] + ' &'
    # if self.verbose:
    #     print 'starting video with command:', cmd
    # os.system(cmd)
    self.load(vidPath)
    self.start()

  def _onStop(self):
    # cmd = 'pkill omxplayer'
    # if self.verbose:
    #     print 'killing video with command:', cmd
    # os.system(cmd)
    self.stop()

  def _onLoad(self, no):
    try:
      no = int(no)
    except:
      no = 0

    if no < 0 or no >= len(self.vidPaths):
        print '[HohVidStarter] invalid load value:', no
        return

    vidPath = self.vidPaths[no]
    if vidPath == '':
        print '[HohVidStarter] empty video path, not loading anything'
        return

    self.load(vidPath)

  def _onPlay(self):
    # if no < 0 or no >= len(self.vidPaths):
    #     print '[HohVidStarter] invalid play value:', no
    #     return

    # cmd = 'omxplayer ' + self.vidPaths[winner] + ' &'
    # if self.verbose:
    #     print 'starting video with command:', cmd
    # os.system(cmd)
    self.start()
