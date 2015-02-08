from subprocess import Popen, PIPE
from twisted.internet import reactor, defer
from twisted.internet.protocol import Protocol, ClientCreator

import json
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory

class WebsocketClient(WebSocketClientProtocol):
  def onMessage(self, payload, isBinary):
    print(payload)
    payload = json.loads(payload)
    if payload[u'cmd'] == u'PLAY':
      self.vlcControl.play(payload[u'meta'][u'url'].encode('utf8'), payload.get(u'time', 0))

class VLCControl(Protocol):
  def connectionMade(self):
    self.cbs = []
    self.transport.write('hunter2\n')

  def play(self, url, t):
    print('Playing url:', url, 'at time t=', t)
    self.transport.write('stop\nclear\n')
    self.transport.write('add ' + url + '\n')
    self.transport.write('play\n')
    # TODO: make more robust somehow.  polling for is_playing
    # didn't seem to work
    if t > 0:
      reactor.callLater(2.0, self.transport.write, "seek %d\n" % int(t))

def _connected(proto):
  fact = WebSocketClientFactory('ws://localhost:8090', debug=False)
  fact.protocol = WebsocketClient
  WebsocketClient.vlcControl = proto
  reactor.connectTCP('localhost', 8090, fact)

if __name__ == '__main__':
  # Start vlc
  vlc=Popen(['vlc', '-I', 'telnet', '--telnet-host', 'localhost', '--telnet-port', '12345', '--telnet-password', 'hunter2'], stderr=PIPE)
  while not "Listening on host" in vlc.stderr.readline(): pass
  d=ClientCreator(reactor, VLCControl).connectTCP('localhost', 12345)
  d.addCallback(_connected)
  reactor.run()
