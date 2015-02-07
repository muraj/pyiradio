import json
import heapq
from twisted.web import resource

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
    return srcid +'-'+ trackid

  def getTrack(self, srcid, trackid, default=None):
    return self.uset.get(self._hash_track(srcid, trackid), default)

  def peeknext(self, n=1):
    return heapq.nsmallest(n, self.heap)

class PlaylistResource(resource.Resource):

  def __init__(self, playlist):
    self.playlist = playlist

  def render_GET(self, req):
    tracks = []
    for track in self.playlist.peeknext(len(self.playlist)):
      tracks.append(track.as_dict())
    return json.dumps(tracks)
