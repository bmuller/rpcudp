import logging
import asyncio
from rpcudp.protocol import RPCProtocol


class RPCServer(RPCProtocol):
    def rpc_sayhi_quickly(self, sender, name):
        return "Hello %s, you live at %s:%i" % (name, sender[0], sender[1])

    @asyncio.coroutine
    def rpc_sayhi_slowly(self, sender, name):
        yield from asyncio.sleep(2)
        return "Hello %s, you live at %s:%i" % (name, sender[0], sender[1])


logging.basicConfig(level=logging.DEBUG)
loop = asyncio.get_event_loop()
loop.set_debug(True)

# listen for requests
listen = loop.create_datagram_endpoint(RPCServer, local_addr=('127.0.0.1', 1234))
transport, protocol = loop.run_until_complete(listen)


try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

transport.close()
loop.close()
