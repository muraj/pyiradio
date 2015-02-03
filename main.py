from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerFactory, listenWS
from twisted.web import server, resource, static
from twisted.python import log
import sys

from PlayerController import PlayerController, Track
from Playlist import PlaylistResource

if __name__ == '__main__':
  log.startLogging(sys.stdout)
  factory = WebSocketServerFactory("ws://localhost:8090", debug=True)
  factory.protocol = PlayerController
  reactor.listenTCP(8090, factory)

  root = resource.Resource()
  root.putChild('playlist', PlaylistResource(PlayerController.playList))
  root.putChild('index', static.File('.'))
  reactor.listenTCP(8080, server.Site(root))

  mock_playlist = [Track('yt', 'ndiD8V7zpAs', 201), Track('yt', 'PfrsvfcZ8ZE', 68)]

  for t in mock_playlist:
    PlayerController.queue(t)

  PlayerController.play_next()

  reactor.run()
