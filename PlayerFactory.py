import time
import random

from autobahn.twisted.websocket import WebSocketServerFactory
from twisted.python import log
from twisted.internet import reactor

from ViewerController import ViewerController
from PlayerController import PlayerController
from Playlist import Playlist
from Track import Track

class ViewerFactory(WebSocketServerFactory):

  def __init__(self, *args, **kwargs):
    WebSocketServerFactory.__init__(self, *args, **kwargs)
    self.controllers = []
    self.protocol = ViewerController

  def addController(self, ctrlr):
    self.controllers.append(ctrlr)

  def removeController(self, ctrlr):
    if ctrlr in self.controllers:
      self.controllers.remove(ctrlr)

  def broadcast(self, cmd, **kwargs):
    log.msg('Broadcasting '+cmd+': ' + str(kwargs))
    for c in self.controllers:
      c.sendCommand(cmd, **kwargs)

class PlayerFactory(ViewerFactory):

  MEDIA_CHANGE_DELAY = 2.0
  MAX_DURATION = 480.0  # 8 minutes
  MIN_DURATION = 30.0   # 30 seconds

  def __init__(self, *args, **kwargs):
    ViewerFactory.__init__(self, *args, **kwargs)
    self.protocol = PlayerController
    self.playList = kwargs.get('playlist', Playlist())
    self.history = kwargs.get('history', set())
    self.currentTrack = None
    self.lastChanged = 0

  def trackFinished(self, track):
    # Add the track to history and play the next track!
    self.history.add((track.srcId, track.trackId, track.duration))
    self.play_next()

  def queue(self, track):
    if not self.MIN_DURATION < track.duration < self.MAX_DURATION:
      return False
    if self.playList.push(track):
      self.broadcast('PLAYLIST-ADD', track=track.as_dict())
      return True
    return False

  def upvote(self, srcid, trackid, id):
    if self.playList.upvote(srcid, trackid, id):
      self.broadcast('PLAYLIST-CHANGE',
        track=self.playList.getTrack(srcid, trackid).as_dict())
      return True
    return False

  def downvote(self, srcid, trackid, id):
    if self.playList.downvote(srcid, trackid, id):
      self.broadcast('PLAYLIST-CHANGE',
        track=self.playList.getTrack(srcid, trackid).as_dict())
      return True
    return False

  def play(self, track):
    log.msg('Playing track:' + str(track.as_dict()))
    self.currentTrack = track
    self.lastChanged = time.time()
    self.broadcast('PLAY', srcId=track.srcId, trackId=track.trackId)
    # Approximate finishing a track and tell the api
    reactor.callLater(track.duration + self.MEDIA_CHANGE_DELAY,
      self.trackFinished, track)

  def play_next(self):
    if len(self.playList) > 0:
      self.play(self.playList.pop())
    elif len(self.history) > 0:
      t = random.sample(self.history, 1)[0]
      t = Track(t[0], t[1], t[2])
      self.play(t)
    else: # No tracks to play, try again in 1 second
      reactor.callLater(1, self.play_next)

  def buildTrack(self, srcid, trackid):
    # Query the srcid api for the duration/metadata of the track
    # then build track.  Return a deferred while the track is being built
    return defer.succeed(Track(srcid, trackid, 30)) # TODO: replace 30 with real duration
