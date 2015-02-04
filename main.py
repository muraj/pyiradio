from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerFactory, listenWS
from twisted.web import server, resource, static
from twisted.python import log
import sys


from PlayerFactory import PlayerFactory
from Track import Track
from Playlist import PlaylistResource

if __name__ == '__main__':
  log.startLogging(sys.stdout)
  factory = PlayerFactory("ws://localhost:8090", debug=True)
  reactor.listenTCP(8090, factory)

  root = resource.Resource()
  root.putChild('playlist', PlaylistResource(factory.playList))
  root.putChild('index', static.File('.'))
  reactor.listenTCP(8080, server.Site(root))

  mock_playlist = [Track('yt', 'ndiD8V7zpAs', 201), Track('yt', 'PfrsvfcZ8ZE', 68)]

  for t in mock_playlist:
    factory.queue(t)

  factory.play_next()

  reactor.run()
