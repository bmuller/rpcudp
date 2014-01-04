from rpcudp.protocol import RPCProtocol
from twisted.python import log
from twisted.internet import reactor
import sys

log.startLogging(sys.stdout)

class RPCServer(RPCProtocol):
    noisy = True
    def rpc_sayhi(self, sender, name):
        # This could return a Deferred as well. sender is (ip, port)
        return "Hello %s, you live at %s:%i" % (name, sender[0], sender[1])

reactor.listenUDP(1234, RPCServer())

class RPCClient(RPCProtocol):
    noisy = True
    def handleResult(self, result):
        if result[0]:
            print "Success! %s" % result[1]
        else:
            print "Response not received."

client = RPCClient()
reactor.listenUDP(4567, client)
client.sayhi(('127.0.0.1', 1234), "Snake Plissken").addCallback(client.handleResult)

reactor.run()
