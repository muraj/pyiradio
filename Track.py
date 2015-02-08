class Track(object):
  def __init__(self, srcId, trackId, duration, meta={}):
    self.srcId = srcId
    self.trackId = trackId
    self.duration = duration
    self.score = 0
    self.upvote_ids = set()
    self.downvote_ids = set()
    self.meta = meta

  def addMeta(self, key, val):
    self.meta[key] = val

  def as_dict(self, meta=True):
    ret = { 'srcId':self.srcId, 'trackId':self.trackId,
            'duration':self.duration, 'score':self.score }
    if meta: ret['meta'] = self.meta
    return ret

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

def youtubeTrackBuilder(srcid, trackid):
  import json
  from twisted.web.client import getPage
  def _parseYT(body):
    body = json.loads(body)[u'entry']
    dur = float(body[u'media$group'][u'yt$duration'][u'seconds'])
    t=Track(srcid, trackid, dur)
    t.addMeta('title', body[u'title'][u'$t'])
    t.addMeta('creator', body[u'author'][0][u'name'][u'$t'])
    t.addMeta('url', 'http://youtu.be/' + trackid)
    return t
  d=getPage("https://gdata.youtube.com/feeds/api/videos/%s?alt=json&v=2" % trackid)
  d.addCallback(_parseYT)
  return d

def soundCloudBuilder(srcid, trackid):
  import json
  from twisted.web.client import getPage
  clientid = 'YOUR_CLIENTID_HERE'
  def _parseSC(body):
    body = json.loads(body)
    t=Track(srcid, trackid, body[u'duration'])
    t.addMeta('title', body[u'title'])
    t.addMeta('creator', body[u'user'][u'username'])
    t.addMeta('url', body[u'permalink_url'])
    return t
  d=getPage("http://api.soundcloud.com/tracks/%s.json?client_id=%s" % (trackid, clientid))
  d.addCallback(_parseSC)
  return d
