import asyncio
import contextlib
import logging
from asyncio.exceptions import CancelledError

from rpcudp.protocol import RPCProtocol

logging.basicConfig(level=logging.DEBUG)

rpc = RPCProtocol()


@rpc.method
def rpc_sayhi_quickly(sender, name):
    return f"Hello {name}, you live at {sender[0]}:{sender[1]}"


@rpc.method
async def rpc_sayhi_slowly(sender, name):
    await asyncio.sleep(2)
    return f"Hello {name}, you live at {sender[0]}:{sender[1]}"


async def main():
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: rpc, local_addr=("127.0.0.1", 1234)
    )

    try:
        with contextlib.suppress(CancelledError):
            await asyncio.Event().wait()
    finally:
        transport.close()


asyncio.run(main())
