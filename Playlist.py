import heapq

class Playlist(object):
  def __init__(self):
    self.heap = []
    self.uset = dict()

  def __len__(self):
    return len(self.heap)

  def push(self, track):
    h = hash(track.srcId + track.trackId)
    if not h in self.uset:
      heapq.heappush(self.heap, track)
      self.uset[h] = track
      return True
    return False

  def pop(self):
    if len(self.heap) == 0: return None
    t = heapq.heappop(self.heap)
    del self.uset[hash(t.srcId + t.trackId)]
    return t

  def upvote(self, srcid, trackid, id):
    h = hash(track.srcId + track.trackId)
    t = self.uset[h]
    if not t.upvote(id): return False
    heapq.heapify(self.heap)  # Use sift up for better O(nlgn)
    return True

  def downvote(self, srcid, trackid, id):
    h = hash(track.srcId + track.trackId)
    t = self.uset[h]
    if not t.downvote(id): return False
    heapq.heapify(self.heap)  # Use sift down for O(n)
    return True
