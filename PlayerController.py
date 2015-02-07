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

  def on_upvote(self, **kwargs):
    # Check if this ip already voted
    # if not, add to upvote and broadcast new score to everyone
    #PlayerController.playList.upvote(srcid, trackid, id)
    pass

  def on_downvote(self, **kwargs):
    # if not, add to downvote and broadcast new score to everyone
    #PlayerController.playList.downvote(srcid, trackid, id)
    if self.factory.playList.downvote(srcid, trackid, id):
      self.factory.broadcast('PLAYLIST_CHANGE',
        track=self.factory.getTrack(srcid, trackid).as_dict())

  def on_auth(self, **kwargs):
    # Check some user database for auth
    # TODO: Replace with oauth or something
    self.auth = True
    self.sendCommand('AUTH', success=self.auth)

  def on_add(self, **kwargs):
    if not self.auth: return
    # Get track information (duration) and add it to playlist
    #if track.duration > ####: return
    #PlayerController.playList.push(track)
