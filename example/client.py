from __future__ import print_function

from rpcudp.protocol import RPCProtocol
from twisted.python import log
from twisted.internet import reactor
import sys

log.startLogging(sys.stdout)


class RPCClient(RPCProtocol):
    noisy = True
    def handleResult(self, result):
        if result[0]:
            print("Success! %s" % result[1])
        else:
            print("Response not received.")

client = RPCClient()
reactor.listenUDP(4567, client)
client.sayhi(('127.0.0.1', 1234), "Snake Plissken").addCallback(client.handleResult)

reactor.run()
