import time
import random
from twisted.internet import reactor
from twisted.python import log

from ViewerController import ViewerController
from Track import Track
from Playlist import Playlist

class PlayerController(ViewerController):
  # config constants
  MEDIA_CHANGE_DELAY = 2
  # Class variables
  playList = Playlist()
  history = set()
  currentTrack = None
  lastChanged = 0

  def onOpen(self):
    ViewerController.onOpen(self)
    self.auth = False
    # Get currently playing song and time index for newly connected person
    if PlayerController.currentTrack:
      t = time.time() - PlayerController.lastChanged
      t = min(t, PlayerController.currentTrack.duration)
      self.sendCommand('PLAY', PlayerController.currentTrack.srcId,
        PlayerController.currentTrack.trackId, str(t))

  def on_upvote(self, *params):
    # Check if this ip already voted
    # if not, add to upvote and broadcast new score to everyone
    #PlayerController.playList.upvote(srcid, trackid, id)
    pass

  def on_downvote(self, *params):
    # Check if this ip already voted
    # if not, add to downvote and broadcast new score to everyone
    #PlayerController.playList.downvote(srcid, trackid, id)
    pass

  def on_auth(self, *params):
    # Check some user database for auth
    self.auth = True

  def on_add(self, *params):
    if not self.auth: return
    # Get track information (duration) and add it to playlist
    #if track.duration > ####: return
    #PlayerController.playList.push(track)

  @staticmethod
  def trackFinished(track):
    # Called when the current track is done
    log.msg('Track finished:' + str(track))
    PlayerController.history.add((track.srcId, track.trackId, track.duration))
    PlayerController.play_next()

  @staticmethod
  def queue(track):
    PlayerController.playList.push(track)

  @staticmethod
  def play(track):
    log.msg('Playing track:' + str(track))
    PlayerController.currentTrack = track
    PlayerController.lastChanged = time.time()
    PlayerController.broadcast('PLAY', track.srcId, track.trackId)
    reactor.callLater(track.duration + PlayerController.MEDIA_CHANGE_DELAY, PlayerController.trackFinished, track)

  @staticmethod
  def play_next():
    if len(PlayerController.playList) > 0:
      PlayerController.play(PlayerController.playList.pop())
    elif len(PlayerController.history) > 0:
      # Pick randomly from history
      t = random.sample(PlayerController.history, 1)[0]
      t = Track(t[0], t[1], t[2])
      PlayerController.play(t)
    else:
      reactor.callLater(1, PlayerController.play_next)
