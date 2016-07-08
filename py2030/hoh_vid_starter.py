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
    self.interface.hohPauseEvent += self._onPause
    self.interface.hohSeekEvent += self._onSeek


  def unload(self):
    if self.player:
      self.player.quit()
      self.player = None

  def load(self, videoPath):
    # close existing video
    if self.player:
      self.unload()

    if self.verbose:
      print '[HohVidStarter#load] loading player with:', videoPath

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

  def seek(self, pos):
    if not self.player:
      print '[HohVidStarter#seek] No video loaded'
      return

    try:
        pos = float(pos)
    except ValueError as err:
        print '[HohVidStarter#seek] invalid pos value:', pos
        return

    if self.verbose:
      print '[HohVidStarter#seek] self.player.set_position() with:', pos

    self.player.set_position(pos)

  def _noToVidPath(self, no):
    # make sure we have an int
    try:
      no = int(no)
    except:
      return ''

    # make sure the int is not out of bounds for our array
    if no < 0 or no >= len(self.vidPaths):
      print '[HohVidStarter] invalid video number:', no
      return ''

    return self.vidPaths[no]


  #
  # Callback methods
  #

  def _onStart(self, no):
    vidPath = self._noToVidPath(no)

    if vidPath == '':
        print '[HohVidStarter] empty video path, not starting anything'
        return

    self.load(vidPath)
    self.start()

  def _onStop(self):
    self.stop()

  def _onLoad(self, no):
    vidPath = self._noToVidPath(no)

    if vidPath == '':
        print '[HohVidStarter] empty video path, not loading anything'
        return

    # load specified video
    self.load(vidPath)

  def _onPlay(self):
    self.start()

  def _onPause(self):
    self.pause()

  def _onSeek(self, pos):
    self.seek(pos)
