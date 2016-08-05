import os
from hashlib import sha1
from base64 import b64encode
import asyncio
import logging

import umsgpack

from rpcudp.exceptions import MalformedMessage


log = logging.getLogger('rpcudp')


class RPCProtocol(asyncio.DatagramProtocol):
    def __init__(self, waitTimeout=5):
        """
        @param waitTimeout: Consider it a connetion failure if no response
        within this time window.
        """
        self._waitTimeout = waitTimeout
        self._outstanding = {}

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, datagram, address):
        log.debug("received datagram from %s", address)
        asyncio.ensure_future(self._solveDatagram(datagram, address))
    
    @asyncio.coroutine
    def _solveDatagram(self, datagram, address):
        if len(datagram) < 22:
            log.warning("received datagram too small from %s, ignoring", address)
            return

        msgID = datagram[1:21]
        data = umsgpack.unpackb(datagram[21:])

        if datagram[:1] == b'\x00':
            # schedule accepting request and returning the result
            asyncio.ensure_future(self._acceptRequest(msgID, data, address))
        elif datagram[:1] == b'\x01':
            self._acceptResponse(msgID, data, address)
        else:
            # otherwise, don't know the format, don't do anything
            log.debug("Received unknown message from %s, ignoring", address)

    def _acceptResponse(self, msgID, data, address):
        msgargs = (b64encode(msgID), address)
        if msgID not in self._outstanding:
            log.warning("received unknown message %s from %s; ignoring", *msgargs)
            return
        log.debug("received response %s for message id %s from %s", data, *msgargs)
        f, timeout = self._outstanding[msgID]
        timeout.cancel()
        f.set_result((True, data))
        del self._outstanding[msgID]

    @asyncio.coroutine
    def _acceptRequest(self, msgID, data, address):
        if not isinstance(data, list) or len(data) != 2:
            raise MalformedMessage("Could not read packet: %s" % data)
        funcname, args = data
        f = getattr(self, "rpc_%s" % funcname, None)
        if f is None or not callable(f):
            msgargs = (self.__class__.__name__, funcname)
            log.warning("%s has no callable method rpc_%s; ignoring request", *msgargs)
            return

        if not asyncio.iscoroutinefunction(f):
            f = asyncio.coroutine(f)
        response = yield from f(address, *args)
        log.debug("sending response %s for msg id %s to %s", response, b64encode(msgID), address)
        txdata = b'\x01' + msgID + umsgpack.packb(response)
        self.transport.sendto(txdata, address)

    def _timeout(self, msgID):
        args = (b64encode(msgID), self._waitTimeout)
        log.error("Did not received reply for msg id %s within %i seconds", *args)
        self._outstanding[msgID][0].set_result((False, None))
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
            log.debug("calling remote function %s on %s (msgid %s)", name, address, b64encode(msgID))
            self.transport.sendto(txdata, address)

            loop = asyncio.get_event_loop()
            f = loop.create_future() if hasattr(loop, 'create_future') else asyncio.Future()
            timeout = loop.call_later(self._waitTimeout, self._timeout, msgID)
            self._outstanding[msgID] = (f, timeout)
            return f
        return func
