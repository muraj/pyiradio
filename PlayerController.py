import time
from ViewerController import ViewerController

class PlayerController(ViewerController):
  def __init__(self, *args, **kwargs):
    ViewerController.__init__(self, *args, **kwargs)
    self.auth = False
  def onOpen(self):
    ViewerController.onOpen(self)
    self.auth = False
    # Get currently playing song and time index for newly connected person
    track = self.factory.currentTrack
    if track:
      t = time.time() - self.factory.lastChanged
      t = min(t, track.duration)
      self.sendCommand('PLAY', srcId=track.srcId,
        trackId=track.trackId, time=t)

"""
  def on_upvote(self, **kwargs):
    self.factory.upvote(srcid, trackid, id)

  def on_downvote(self, **kwargs):
    self.factory.downvote(srcid, trackid, id)

  def on_auth(self, **kwargs):
    # Check some user database for auth
    # TODO: Replace with oauth or something
    self.auth = True
    self.sendCommand('AUTH', success=self.auth)

  def on_queue(self, **kwargs):
    if not self.auth: return
    d=self.factory.buildTrack(srcid, trackid)
    d.addCallback(self.factory.queue)
"""
