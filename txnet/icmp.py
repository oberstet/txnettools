"""
Internet Control Message Protocol implementation.
"""
import socket

from zope.interface import implements

from twisted.internet.udp import Port as UDPPort
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.interfaces import ISystemHandle

from impacket import ImpactDecoder, ImpactPacket

from txnet import util
from txnet.interfaces import IICMPTransport


ECHO_REPLY = 0
# 1 & 2 are reserved
DESTINATION_UNREACHABLE = 3
SOURCE_QUENCH = 4
REDIRECT_MESSAGE = 5
ALTERNATE_HOST_ADDRESS = 6
# 7 is reserved
ECHO_REQUEST = 8
ROUTER_ADVERTISEMENT = 9
ROUTER_SOLICITATION = 10
TIME_EXCEEDED = 11
PARAMETER_PROBLEM_BAD_IP_HEADER = 12
TIMESTAMP = 13
TIMESTAMP_REPLY = 14
INFORMATION_REQUEST = 15
INFORMATION_REPLY = 16
ADDRESS_MASK_REQUEST = 17
ADDRESS_MASK_REPLY = 18
# 19 - 29 are reserved
TRACEROUTE = 30
DATAGRAM_CONVERSION_ERROR = 31
MOBILE_HOST_REDIRECT = 32
WHERE_ARE_YOU = 33
HERE_I_AM = 34
MOBILE_REGISTRATION_REQUEST = 35
MOBILE_REGISTRATION_REPLY = 36
DOMAIN_NAME_REQUEST = 37
DOMAIN_NAME_REPLY = 38
SKIP_ALGORITHM_DISCOVERY_PROTOCOL = 39
PHOTURIS_SECURITY_FAILURES = 40
# 41 is experimental
# 42 - 255 are reserved


ICMP_MESSAGES = {
    ECHO_REPLY: {
        0: "Echo reply"
        },
    DESTINATION_UNREACHABLE: {
        0: "Destination network unreachable",
        1: "Destination host unreachable",
        2: "Destination protocol unreachable",
        3: "Destination port unreachable",
        4: "Fragmentation required, and DF flag set",
        5: "Source route failed",
        6: "Destination network unknown",
        7: "Destination host unknown",
        8: "Source host isolated",
        9: "Network administratively prohibited",
        10: "Host administratively prohibited",
        11: "Network unreachable for TOS",
        12: "Host unreachable for TOS",
        13: "Communication administratively prohibited",
        },
    SOURCE_QUENCH: {
        0: "Source quench (congestion control)",
        },
    REDIRECT_MESSAGE: {
        0: "Redirect Datagram for the Network",
        1: "Redirect Datagram for the Host",
        2: "Redirect Datagram for the TOS & network",
        3: "Redirect Datagram for the TOS & host",
        },
    ALTERNATE_HOST_ADDRESS: {
        None: "Alternate Host Address",
        },
    ECHO_REQUEST: {
        0: "Echo request",
        },
    ROUTER_ADVERTISEMENT: {
        0: "Router Advertisement",
        },
    ROUTER_SOLICITATION: {
        0: "Router discovery/selection/solicitation",
        },
    TIME_EXCEEDED: {
        0: "TTL expired in transit",
        1: "Fragment reassembly time exceeded",
        },
    PARAMETER_PROBLEM_BAD_IP_HEADER: {
        0: "Pointer indicates the error",
        1: "Missing a required option",
        2: "Bad length",
        },
    TIMESTAMP: {
        0: "Timestamp",
        },
    TIMESTAMP_REPLY: {
        0: "Timestamp reply",
        },
    INFORMATION_REQUEST: {
        0: "Information Request",
        },
    INFORMATION_REPLY: {
        0: "Information Reply",
        },
    ADDRESS_MASK_REQUEST: {
        0: "Address Mask Request",
        },
    ADDRESS_MASK_REPLY: {
        0: "Address Mask Reply",
        },
    TRACEROUTE: {
        0: "Information Request",
        },
    DATAGRAM_CONVERSION_ERROR: {
        None: "Datagram Conversion Error",
        },
    MOBILE_HOST_REDIRECT: {
        None: "Mobile Host Redirect",
        },
    WHERE_ARE_YOU: {
        None: "Where-Are-You",
        },
    HERE_I_AM: {
        None: "Here-I-Am",
        },
    MOBILE_REGISTRATION_REQUEST: {
        None: "Mobile Registration Request",
        },
    MOBILE_REGISTRATION_REPLY: {
        None: "Mobile Registration Reply",
        },
    DOMAIN_NAME_REQUEST: {
        None: "Domain Name Request",
        },
    DOMAIN_NAME_REPLY: {
        None: "Domain Name Reply",
        },
    SKIP_ALGORITHM_DISCOVERY_PROTOCOL: {
        None: "SKIP Algorithm Discovery Protocol",
        },
    PHOTURIS_SECURITY_FAILURES: {
        None: "Photuris, Security failures",
        },
    }


class Packet(object):
    """
    A wrapper for the impacket packet code.
    """
    def __init__(self, src="127.0.0.1", dst="127.0.0.1", type=None, code=None,
                 ttl=1200, payload="txNetTools", rawPacket=None):
        self.src = src
        self.dst = dst
        self.type = type
        self.code = code
        self.ttl = ttl
        self.payload = payload
        if rawPacket:
            self.decodePacket(rawPacket)
            return
        if type is not None:
            self.encodePacket(src, dst, type, code, ttl, payload)

    def encodePacket(self, src, dst, type, code, ttl, payload):
        payload = ImpactPacket.Data(payload)
        icmpDatagram = ImpactPacket.ICMP()
        icmpDatagram.set_icmp_type(type)
        if code:
            icmpDatagram.set_icmp_code(code)
        icmpDatagram.set_icmp_lifetime(ttl)
        icmpDatagram.set_icmp_ttime(ttl)
        icmpDatagram.contains(payload)
        ipDatagram = ImpactPacket.IP()
        ipDatagram.set_ip_src(src)
        ipDatagram.set_ip_dst(dst)
        ipDatagram.contains(icmpDatagram)
        self.raw = ipDatagram.get_packet()

    def decodePacket(self, rawPacket):
        ipDecoded = ImpactDecoder.IPDecoder().decode(rawPacket)
        self.src = ipDecoded.get_ip_src()
        self.dst = ipDecoded.get_ip_dst()
        icmpDecoded = ipDecoded.child()
        self.type = icmpDecoded.get_icmp_type()
        self.code = icmpDecoded.get_icmp_code()
        self.raw = ipDecoded.get_packet()
        print icmpDecoded.get_icmp_gwaddr()
        print icmpDecoded.get_icmp_lifetime()
        print icmpDecoded.get_icmp_ttime()
        print "src:", self.src
        print "dst:", self.dst

    def getDatagram(self):
        return self.raw

    def getMessage(self, type=None, code=None):
        if not type:
            type = self.type
        if not code:
            code = self.code
        # XXX this needs a bunch of unit tests
        return ICMP_MESSAGES[type][code]


class ICMP(DatagramProtocol):
    """
    """
    def datagramReceived(self, datagram, address):
        host, port = address
        print "Received %s from %s:%s" % (repr(datagram), host, port)
        packet = Packet(rawPacket=datagram)
        print packet.getMessage()

    def sendEchoRequest(self):
        pass


class Port(UDPPort):
    """
    ICMP port, listening for packets.
    """

    implements(IICMPTransport, ISystemHandle)

    addressFamily = socket.AF_INET
    socketType = socket.SOCK_RAW
    socketProtocol = socket.IPPROTO_ICMP
    maxThroughput = 256 * 1024 # max bytes we read in one eventloop iteration

    def createInternetSocket(self):
        """
        We override the BasePort's createInternetSocket method so that we can
        set the IP protocol to ICMP.
        """
        s = socket.socket(
            self.addressFamily, self.socketType, self.socketProtocol)
        #s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        s.setblocking(0)
        util.setCloseOnExec(s.fileno())
        return s
