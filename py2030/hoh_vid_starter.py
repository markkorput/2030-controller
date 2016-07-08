from py2030.interface import Interface
try:
    from omxplayer import OMXPlayer
except:
    print '[HohVidStarter] no omxplayer'
    OMXPlayer = None

import os

class HohVidStarter:
  def __init__(self, options = {}):
    # params
    # self.options = options
    # config
    self.interface = options['interface'] if 'interface' in options else Interface.instance()
    self.verbose = 'verbose' in options and options['verbose']
    self.player = None
    self.hostname = options['hostname'] if 'hostname' in options else ''
    # get video paths
    self.vidPaths = []
    self.vidPaths = options['vids'] if 'vids' in options else []
    print '[HohVidStarter] video paths:', self.vidPaths

  def __del__(self):
      if self.player:
          self.unload()

  def setup(self):

    # register callbacks
    self.interface.hohStartEvent += self._onStart
    self.interface.hohLoadEvent += self._onLoad
    self.interface.hohPlayEvent += self._onPlay
    self.interface.hohStopEvent += self._onStop
    self.interface.hohPauseEvent += self._onPause
    self.interface.hohSeekEvent += self._onSeek
    self.interface.hohSpeedEvent += self._onSpeed


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
        self.player = OMXPlayer(videoPath, args=['--no-osd', '--adev', 'local', '-b'])

  def start(self):
    if not self.player:
      print '[HohVidStarter#start] No video loaded'
      return
    if self.verbose:
      print '[HohVidStarter#start] self.player.play()'
    # clear console screen
    #print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
    os.system('clear')
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
    # clear console screen
    #print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
    os.system('clear')

    self.player.stop()
    os.system('clear')

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

  def speed(self, speed):
    if not self.player:
      print '[HohVidStarter#speed] No video loaded'
      return

    # speed -1 means 'slower'
    # speed 1 means 'faster'

    if speed == -1:
      if self.verbose:
        print '[HohVidStarter#speed] slower'
      self.player.action(1)
      return

    if speed == 1:
      if self.verbose:
        print '[HohVidStarter#speed] faster'
      self.player.action(2)
      return

    print '[HohVidStarter#speed invalid speed value:', speed

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

  def _onSpeed(self, hostname, speed):
    if hostname != self.hostname:
      # not for us
      return 

    self.speed(speed)
