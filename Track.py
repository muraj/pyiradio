class Track(object):
  def __init__(self, srcId, trackId, duration):
    self.srcId = srcId
    self.trackId = trackId
    self.duration = duration
    self.score = 0
    self.upvote_ids = set()
    self.downvote_ids = set()

  def __hash__(self):
    return hash(self.srcId + self.trackId)

  def __cmp__(self, other):
    if hash(self) == hash(other): return 0
    return other.score - self.score # sort by score, descending

  def upvote(self, id):
    if id in self.upvote_ids: return False
    try:
      self.downvote_ids.remove(id)
    except:
      pass
    self.score += 1
    self.upvote_ids.add(id)
    return True

  def downvote(self, id):
    if id in self.downvote_ids: return False
    try:
      self.upvote_ids.remove(id)
    except:
      pass
    self.score -= 1
    self.downvote_ids.add(id)
    return True
