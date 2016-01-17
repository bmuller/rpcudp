from __future__ import print_function

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

reactor.run()
