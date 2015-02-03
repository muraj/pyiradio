from autobahn.twisted.websocket import WebSocketServerProtocol
from twisted.internet.task import LoopingCall
from twisted.python import log

class ViewerController(WebSocketServerProtocol):
  controllers = []

  def onOpen(self):
    ViewerController.controllers.append(self)
    #LoopingCall(self.ping).start(10)   # Start pinging

  def onMessage(self, payload, isBinary):
    if isBinary: return
    payload = payload.split(',')
    getattr(self, 'on_' + payload[0].lower(), lambda *p: None)(*payload[1:])

  def onClose(self, wasClean, code, reason):
    if self in ViewerController.controllers:
      ViewerController.controllers.remove(self)

  def ping(self):
    self.sendMessage('PING')

  def on_pong(self, *params):
    pass

  def sendCommand(self, cmd, *params):
    params = [ str(p) for p in params ]
    log.msg('****** SENDING COMMAND: ' + cmd + ': ' + ','.join(params))
    params = [str(cmd)] + [ str(p) for p in params ]
    self.sendMessage(','.join(params))

  @staticmethod
  def broadcast(cmd, *params):
    log.msg('Broadcasting '+cmd+': ' + ','.join(params))
    for ctrlr in ViewerController.controllers:
      ctrlr.sendCommand(cmd, *params)
