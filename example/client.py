import logging
import asyncio
from rpcudp.protocol import RPCProtocol


async def sayhi(protocol, address):
    # call rpc that returns immediately
    result = await protocol.sayhi_quickly(address, "Fast Snake Plissken")
    print(result[1] if result[0] else "No response received.")

    # call rpc that delays for a bit
    result = await protocol.sayhi_slowly(address, "Slow Snake Plissken")
    print(result[1] if result[0] else "No response received.")


logging.basicConfig(level=logging.DEBUG)
loop = asyncio.get_event_loop()
loop.set_debug(True)

# Start local UDP server to be able to handle responses
listen = loop.create_datagram_endpoint(RPCProtocol, local_addr=('127.0.0.1', 4567))
transport, protocol = loop.run_until_complete(listen)

# Call remote UDP server to say hi
func = sayhi(protocol, ('127.0.0.1', 1234))
loop.run_until_complete(func)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

transport.close()
loop.close()
