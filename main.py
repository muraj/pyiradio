from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerFactory, listenWS
from twisted.web import server, resource, static
from twisted.python import log
import sys

from PlayerFactory import PlayerFactory
from Track import youtubeTrackBuilder
from Playlist import PlaylistResource, QueueResource, VoteResource

from zope.interface import implements
from twisted.cred.portal import IRealm, Portal
from twisted.cred.checkers import FilePasswordDB
from twisted.web.guard import HTTPAuthSessionWrapper, DigestCredentialFactory

class ProtectedResource(object):

  class PublicHTMLRealm(object):
    implements(IRealm)
    def __init__(self, res):
      self.resource = res

    def requestAvatar(self, avatarId, mind, *interfaces):
      if resource.IResource in interfaces:
        return (resource.IResource, self.resource, lambda: None)
      raise NotImplementedError()

  def __init__(self, checkers):
    self.checkers = checkers

  def protect_resource(self, res, realm='Auth'):
    portal = Portal(ProtectedResource.PublicHTMLRealm(res), self.checkers)
    credFactory = DigestCredentialFactory('md5', realm)
    return HTTPAuthSessionWrapper(portal, [credFactory])


if __name__ == '__main__':
  log.startLogging(sys.stdout)
  factory = PlayerFactory("ws://localhost:8090", debug=True)
  factory.addTrackBuilder('yt', youtubeTrackBuilder)
  reactor.listenTCP(8090, factory)
  pr = ProtectedResource([FilePasswordDB('httpd.password')])

  root = resource.Resource()
  root.putChild('playlist', PlaylistResource(factory.playList))
  root.putChild('index.html', static.File('index.html'))
  root.putChild('queue', pr.protect_resource(QueueResource(factory)))
  root.putChild('auth', pr.protect_resource(static.Data('SUCCESS', 'text/html')))
  root.putChild('vote',  VoteResource(factory))
  reactor.listenTCP(8080, server.Site(root))

  mock_playlist = [('yt', 'ndiD8V7zpAs'), ('yt', 'PfrsvfcZ8ZE')]

  for sid, tid in mock_playlist:
    factory.buildTrack(sid, tid).addCallback(factory.queue)

  factory.play_next()

  reactor.run()
