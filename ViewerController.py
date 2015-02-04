import json
from autobahn.twisted.websocket import WebSocketServerProtocol
from twisted.internet.task import LoopingCall
from twisted.python import log

class ViewerController(WebSocketServerProtocol):

  def __init__(self, *args, **kwargs):
    pass

  def onOpen(self):
    self.factory.addController(self)
    #LoopingCall(self.ping).start(10)   # Start pinging

  def onMessage(self, payload, isBinary):
    if isBinary: return
    payload = json.loads(payload)
    cmd = payload[u'cmd'].lower().decode('utf8')
    # TODO: Capture error
    getattr(self, 'on_' + cmd, lambda **k: None)(**payload)

  def onClose(self, wasClean, code, reason):
    self.factory.removeController(self)

  def sendCommand(self, cmd, **kwargs):
    kwargs[u'cmd'] = cmd
    payload = json.dumps(kwargs)
    self.sendMessage(payload)
