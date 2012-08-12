from random import randint
import socket
import struct

from twisted.internet.protocol import DatagramProtocol

# needs to be run with sudo, so let's add the dev path
import sys
sys.path.insert(0, ".")

from txnet.icmp import ICMP, Packet, ECHO_REQUEST
from txnet.reactor import reactor


UDP_PORT_MIN = 33434
UDP_PORT_MAX = 33534


def get_remote_port():
    return randint(UDP_PORT_MIN, UDP_PORT_MAX)


class Pinger(ICMP):

    def sendEcho(self):
        print "Sending echo ..."
        src = "192.168.1.1"
        #dst = "127.0.0.1"
        #dst = "192.168.1.1"
        #dst = "192.168.100.1"
        dst = "74.125.45.100"
        self.transport.connect(dst, get_remote_port())
        # Construct a ping packet (with useless payload data).
        packet = Packet(
            src=src, dst=dst, type=ECHO_REQUEST, payload="txNetTools ping")
        raw = packet.getDatagram()
        self.transport.write(packet.getDatagram())

    def startProtocol(self):
        print "Transport is:", self.transport
        print "Transport class is:", self.transport.__class__
        print "self is:", self
        self.sendEcho()

    def connectionRefused(self):
        print "Connection refused ..."
        print "Host:", self.transport.getHost()
        print "Remote host:", self.transport._connectedAddr
        print "Connected:", self.transport.connected
        print "Disconnected:", self.transport.disconnected
        print "Data buffer:", self.transport.dataBuffer


reactor.listenICMP(0, Pinger())
reactor.run()
