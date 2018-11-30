# RPCUDP : [RPC](http://en.wikipedia.org/wiki/Remote_procedure_call) over [UDP](http://en.wikipedia.org/wiki/User_Datagram_Protocol) in Python
[![Build Status](https://secure.travis-ci.org/bmuller/rpcudp.png?branch=master)](https://travis-ci.org/bmuller/rpcudp)

RPC over UDP may seem like a silly idea, but things like the [DHT](http://en.wikipedia.org/wiki/Distributed_hash_table) [Kademlia](http://en.wikipedia.org/wiki/Kademlia) require it.  This project is specifically designed for [asynchronous Python 3](https://docs.python.org/3/library/asyncio.html) code to accept and send remote proceedure calls.

Because of the use of UDP, you will not always know whether or not a procedure call was successfully received.  This isn't considered an exception state in the library, though you will know if a response isn't received by the server in a configurable amount of time.

## Installation

```
pip install rpcudp
```

## Usage
*This assumes you have a working familiarity with [asyncio](https://docs.python.org/3/library/asyncio.html).*

First, let's make a server that accepts a remote procedure call and spin it up.

```python
import asyncio
from rpcudp.protocol import RPCProtocol


class RPCServer(RPCProtocol):
    # Any methods starting with "rpc_" are available to clients.
    def rpc_sayhi(self, sender, name):
        # This could return a Deferred as well. sender is (ip,port)
        return "Hello %s you live at %s:%i" % (name, sender[0], sender[1])

# start a server on UDP port 1234
loop = asyncio.get_event_loop()
listen = loop.create_datagram_endpoint(RPCServer, local_addr=('127.0.0.1', 1234))
transport, protocol = loop.run_until_complete(listen)
loop.run_forever()
```

Now, let's make a client script.  Note that we do need to specify a port for the client as well, since it needs to listen for responses to RPC calls on a UDP port.

```python
import asyncio
from rpcudp.protocol import RPCProtocol


@asyncio.coroutine
def sayhi(protocol, address):
    # result will be a tuple - first arg is a boolean indicating whether a response
    # was received, and the second argument is the response if one was received.
    result = yield from protocol.sayhi(address, "Snake Plissken")
    print(result[1] if result[0] else "No response received.")


# Start local UDP server to be able to handle responses
loop = asyncio.get_event_loop()
listen = loop.create_datagram_endpoint(RPCProtocol, local_addr=('127.0.0.1', 4567))
transport, protocol = loop.run_until_complete(listen)

# Call remote UDP server to say hi
func = sayhi(protocol, ('127.0.0.1', 1234))
loop.run_until_complete(func)
loop.run_forever()
```

You can run this example in the examples folder (client.py and server.py).

## Logging
This library uses the standard [Python logging library](https://docs.python.org/3/library/logging.html).  To see debut output printed to STDOUT, for instance, use:

```python
import logging

log = logging.getLogger('rpcudp')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())
```

## Running Tests
To run tests:

```
pip install -r dev-requirements.txt
python -m unittest
```

## Implementation Details
The protocol is designed to be as small and fast as possible.  Python objects are serialized using [MsgPack](http://msgpack.org/).  All calls must fit within 8K (generally small enough to fit in one datagram packet).

## Compatibility
With version 2.0 compatibility is broken with previous versions. In version 2.0 the method name when making a remote call is always packed as a unicode string. In previous versions, the type of string that method name was depended on the Python version. In order to make instances running on Python 2 (only versions before 3.0 worked with Python 2) and Python 3 compatible with each other the method name is now encoded as a unicode string before being packed, which ensures that [u-msgpack-python](https://github.com/vsergeev/u-msgpack-python) will always pack the it the same way. See [u-msgpack-python#behaviour-notes](https://github.com/vsergeev/u-msgpack-python#behavior-notes) for more information.

If you intend to have instances running on both Python 2 and Python 3 communicating with each other make sure that all strings in the arguments you send are unicode encoded as well to ensure compatibility.
