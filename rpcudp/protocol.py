import os
import umsgpack
from hashlib import sha1
from base64 import b64encode

from twisted.internet import protocol
from twisted.internet import reactor
from twisted.internet import defer
from twisted.python import log

from rpcudp.exceptions import MalformedMessage


class RPCProtocol(protocol.DatagramProtocol):
    noisy = False

    def __init__(self, waitTimeout=5):
        """
        @param waitTimeout: Consider it a connetion failure if no response
        within this time window.
        """
        self._waitTimeout = waitTimeout
        self._outstanding = {}

    def datagramReceived(self, datagram, address):
        if self.noisy:
            log.msg("received datagram from %s" % repr(address))
        if len(datagram) < 22:
            log.msg("received datagram too small from %s, ignoring" % repr(address))
            return

        msgID = datagram[1:21]
        data = umsgpack.unpackb(datagram[21:])

        if datagram[:1] == b'\x00':
            self._acceptRequest(msgID, data, address)
        elif datagram[:1] == b'\x01':
            self._acceptResponse(msgID, data, address)
        else:
            # otherwise, don't know the format, don't do anything
            log.msg("Received unknown message from %s, ignoring" % repr(address))

    def _acceptResponse(self, msgID, data, address):
        msgargs = (b64encode(msgID), address)
        if msgID not in self._outstanding:
            log.err("received unknown message %s from %s; ignoring" % msgargs)
            return
        if self.noisy:
            log.msg("received response for message id %s from %s" % msgargs)
        d, timeout = self._outstanding[msgID]
        timeout.cancel()
        d.callback((True, data))
        del self._outstanding[msgID]

    def _acceptRequest(self, msgID, data, address):
        if not isinstance(data, list) or len(data) != 2:
            raise MalformedMessage("Could not read packet: %s" % data)
        funcname, args = data
        f = getattr(self, "rpc_%s" % funcname, None)
        if f is None or not callable(f):
            msgargs = (self.__class__.__name__, funcname)
            log.err("%s has no callable method rpc_%s; ignoring request" % msgargs)
            return
        d = defer.maybeDeferred(f, address, *args)
        d.addCallback(self._sendResponse, msgID, address)

    def _sendResponse(self, response, msgID, address):
        if self.noisy:
            log.msg("sending response for msg id %s to %s" % (b64encode(msgID), address))
        txdata = b'\x01' + msgID + umsgpack.packb(response)
        self.transport.write(txdata, address)

    def _timeout(self, msgID):
        args = (b64encode(msgID), self._waitTimeout)
        log.err("Did not received reply for msg id %s within %i seconds" % args)
        self._outstanding[msgID][0].callback((False, None))
        del self._outstanding[msgID]

    def __getattr__(self, name):
        if name.startswith("_") or name.startswith("rpc_"):
            return object.__getattr__(self, name)

        try:
            return object.__getattr__(self, name)
        except AttributeError:
            pass

        def func(address, *args):
            msgID = sha1(os.urandom(32)).digest()
            data = umsgpack.packb([name, args])
            if len(data) > 8192:
                msg = "Total length of function name and arguments cannot exceed 8K"
                raise MalformedMessage(msg)
            txdata = b'\x00' + msgID + data
            if self.noisy:
                log.msg("calling remote function %s on %s (msgid %s)" % (name, address, b64encode(msgID)))
            self.transport.write(txdata, address)
            d = defer.Deferred()
            timeout = reactor.callLater(self._waitTimeout, self._timeout, msgID)
            self._outstanding[msgID] = (d, timeout)
            return d
        return func
