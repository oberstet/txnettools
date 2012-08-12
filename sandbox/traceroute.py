from random import randint
import socket
import struct

from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol


UDP_PORT_MIN = 33434
UDP_PORT_MAX = 33534


def get_remote_port():
    return randint(UDP_PORT_MIN, UDP_PORT_MAX)


class Tracerouter(DatagramProtocol):

    sequence = 0

    def setTTL(self, ttl):
        ttl = struct.pack("B", ttl)
        transportSocket = self.transport.getHandle()
        transportSocket.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    def sendProbe(self):
        print "Sending message with sequence of %s ..." % self.sequence
        self.setTTL(self.sequence)
        self.transport.connect("74.125.67.100", get_remote_port())
        # send useless data with an appropriate TTL
        self.transport.write("txNetTools traceroute")

    def startProtocol(self):
        print "Transport is:", self.transport
        print "Transport class is:", self.transport.__class__
        print "self is:", self
        self.sendProbe()

    def datagramReceived(self, data, (host, port)):
        print "received %r from %s:%d" % (data, host, port)
        # let's hit the next router
        self.sequence += 1
        self.sendProbe()

    def connectionRefused(self):
        print "Connection refused ..."
        print "Host:", self.transport.getHost()
        print "Remote host:", self.transport._connectedAddr
        print "Connected:", self.transport.connected
        print "Disconnected:", self.transport.disconnected
        print "Data buffer:", self.transport.dataBuffer

"""
We need to send on UDP and listen on ICMP... so we need two transports, one for
writing (UDP) and one for reading (ICMP). If the Tracerouter DatagramProtocol
subclass was to implement this, we might have to do something like the
following:

We'll need to implement a new Port, similar to twisted.internet.udp.Port.
Perhaps icmp.Port. If we want a traceroute "Port" wrapper, we could create
traceroute.Port, and this would wrap udp.Port and imcp.Port...

This would mean that a Tracerouter DatagramProtocol subclass' trasport
attribute would actually be a traceroute.Port instance. We'd have to do the
following for it:
 * provide two attributes: self.udp and self.icmp ... these would both need
   custom setup ...
 * add a getHandle method that would take a "type" parameter (whose values
   could be "udp" and "icmp") and would return either self.icmp.getHandle() or
   self.udp.getHandle()
 * provide a _bindSocket method that would call self.icmp._bindSocket?
 * XXX what would we do with startReading (it calls the reactor's addReader
   method)?
 * provide a write method that would call self.udp.write
 * provide a doRead method that would call self.icmp.doRead
 * provide a connect method that would call self.udp.connect; would
   self.icmp.connect be called as well?
 * connectionLost would have to call self.udp.connectionLost ... and maybe
   self.icmp.connectionLost too?
 * add a getHost method that would call self.udp.getHandler().getHost()

Things to look at more closely:
 * what is the reactor doing with the port instance? That will give us the best
   clue about which (icmp, udp) to use for what.

We'll need to subclass the posixbase reactor and have it use listenTraceroute.

Hrm... Jeremy Hylton's traceroute does a select.select on the icmp socket...
which makes sense, as that's the one that will be read, so that's what the code
is waiting on...

Look at Twisted's posixbase._Win32Waker... it has two sockets defined (for an
entirely different reason). t.i.base.ReactorBase has a waker attribute that is
None by default. We could write our own waker, subclass PosixReactorBase (and
maybe override installWaker to set the readers), add method for listenICMP, and
then use this reactor. We could call it ExtendedPosixReactor.
"""
reactor.listenUDP(0, Tracerouter())
reactor.run()
