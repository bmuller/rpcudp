# RPCUDP : [RPC](http://en.wikipedia.org/wiki/Remote_procedure_call) over [UDP](http://en.wikipedia.org/wiki/User_Datagram_Protocol) in Python

RPC over UDP may seem like a silly idea, but things like the [DHT](http://en.wikipedia.org/wiki/Distributed_hash_table) [Kademlia](http://en.wikipedia.org/wiki/Kademlia) require it.  This project is specifically designed for asynchronous [Python Twisted](http://twistedmatrix.com) code to accept and send remote proceedure calls.

Because of the use of UDP, you will not always know whether or not a procedure call was successfully received.  This isn't considered an exception state in the library, though you will know if a response isn't received by the server in a configurable amount of time.

## Installation

```
pip install rpcudp
```

## Usage
*This assumes you have a working familiarity with Twisted.*

First, let's make a server that accepts a remote procedure call and spin it up.

```python
from rpcudp.protocol import RPCProtocol
from twisted.internet import reactor

class RPCServer(RPCProtocol):
    # Any methods starting with "rpc_" are available to clients.
    def rpc_sayhi(self, sender, name):
        # This could return a Deferred as well. sender is (ip,port)
        return "Hello %s you live at %s:%i" % (name, sender[0], sender[1])

# start a server on UDP port 1234
reactor.listenUDP(1234, RPCServer())
reactor.run()
```

Now, let's make a client.  Note that we do need to specify a port for the client as well, since it needs to listen for responses to RPC calls on a UDP port.

```python
from rpcudp.protocol import RPCProtocol
from twisted.internet import reactor

class RPCClient(RPCProtocol):
    def handleResult(self, result):
    	# result will be a tuple - first arg is a boolean indicating whether a response
        # was received, and the second argument is the response if one was received.
        if result[0]:
            print "Success! %s" % result[1]
        else:
            print "Response not received."

client = RPCClient()
reactor.listenUDP(5678, client)
client.sayhi(('127.0.0.1', 1234), "Snake Plissken").addCallback(client.handleResult)
reactor.run()
```

You can run this example in the example.py file in the root folder.

## Implementation Details
The protocol is designed to be as small and fast as possible.  Python objects are serialized using [MsgPack](http://msgpack.org/).  All calls must fit within 8K (generally small enough to fit in one datagram packet).

## Compatibility
With version 2.0 compatibility is broken with previous versions. In version 2.0 the method name when making a remote call is always packed as a unicode string. In previous versions, the type of string that method name was depended on the Python version. In order to make instances running on Python 2 and Python 3 compatible with each other the method name is now encoded as a unicode string before being packed, which ensures that [u-msgpack-python](https://github.com/vsergeev/u-msgpack-python) will always pack the it the same way. See [u-msgpack-python#behaviour-notes](https://github.com/vsergeev/u-msgpack-python#behavior-notes) for more information.

If you intend to have instances running on both Python 2 and Python 3 communicating with each other make sure that all strings in the arguments you send are unicode encoded as well to ensure compatibility.
