import asyncio
import logging

from rpcudp.protocol import RPCProtocol

logging.basicConfig(level=logging.DEBUG)


async def sayhi(protocol, address):
    # call rpc that returns immediately
    result = await protocol.sayhi_quickly(address, "Fast Snake Plissken")
    print(result[1] if result[0] else "No response received.")

    # call rpc that delays for a bit
    result = await protocol.sayhi_slowly(address, "Slow Snake Plissken")
    print(result[1] if result[0] else "No response received.")


async def main():
    loop = asyncio.get_event_loop()
    loop.set_debug(True)

    # Start local UDP server to be able to handle responses
    transport, protocol = await loop.create_datagram_endpoint(
        RPCProtocol, local_addr=("127.0.0.1", 4567)
    )

    # Call remote UDP server to say hi
    await sayhi(protocol, ("127.0.0.1", 1234))
    transport.close()


asyncio.run(main())
