import json
import heapq
from twisted.web import resource, server

class Playlist(object):
  def __init__(self):
    self.heap = []
    self.uset = dict()

  def __len__(self):
    return len(self.heap)

  def push(self, track):
    h = self._hash_track(track.srcId, track.trackId)
    if h in self.uset:
      return False
    heapq.heappush(self.heap, track)
    self.uset[h] = track
    return True

  def pop(self):
    if len(self.heap) == 0: return None
    t = heapq.heappop(self.heap)
    del self.uset[self._hash_track(t.srcId, t.trackId)]
    return t

  def upvote(self, srcid, trackid, id):
    t = self.getTrack(srcid, trackid)
    if not (t and t.downvote(id)): return False
    heapq.heapify(self.heap)  # Use sift up for better O(nlgn)
    return True

  def downvote(self, srcid, trackid, id):
    t = self.getTrack(srcid, trackid)
    if not (t and t.downvote(id)): return False
    heapq.heapify(self.heap)  # Use sift down for O(n)
    return True

  def _hash_track(self, srcid, trackid):
    return srcid + '-' + trackid

  def getTrack(self, srcid, trackid, default=None):
    return self.uset.get(self._hash_track(srcid, trackid), default)

  def peeknext(self, n=1):
    return heapq.nsmallest(n, self.heap)

class VoteResource(resource.Resource):

  def __init__(self, playerFactory):
    self.playerFactory = playerFactory

  def render_GET(self, req):
    srcid   = req.args.get('srcid', [None])[0]
    trackid = req.args.get('trackid', [None])[0]
    vote = req.args.get('vote', [None])[0]
    id = req.getClientIP()
    if not (srcid and trackid and vote):
      return '"Invalid arguments"'
    if vote == 'up':
      self.playerFactory.upvote(srcid, trackid, id)
    elif vote == 'down':
      self.playerFactory.downvote(srcid, trackid, id)
    return '' # Something?

  def render_POST(self, req):
    return self.render_GET(req)

class QueueResource(resource.Resource):
  def __init__(self, playerFactory):
    self.playerFactory = playerFactory

  def _finishRender(self, track, req):
    if track:
      req.write(json.dumps(track.as_dict()))
      self.playerFactory.queue(track)
    else:
      req.write('Failed!')
    req.finish()

  def render_GET(self, req):
    srcid   = req.args.get('srcid',   [None])[0]
    trackid = req.args.get('trackid', [None])[0]
    if not (srcid and trackid):
      return '"Invalid arguments"'
    d = self.playerFactory.buildTrack(srcid, trackid)
    d.addCallback(self._finishRender, req)
    d.addErrback(self._finishRender, None, req)
    return server.NOT_DONE_YET

  def render_POST(self, req):
    return self.render_GET(req)

class PlaylistResource(resource.Resource):

  def __init__(self, playlist):
    self.playlist = playlist

  def render_GET(self, req):
    tracks = [ t.as_dict() for t in self.playlist.peeknext(len(self.playlist)) ]
    return json.dumps(tracks)
