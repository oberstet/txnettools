from zope.interface import Interface


class IReactorICMP(Interface):
    """
    ICMP socket methods.
    """
    def listenICMP(port, protocol, interface="", maxPacketSize=8192):
        """
        Connects a given DatagramProtocol to the given numeric ICMP port.

        @return: obect which provides L{IListeningPort}.
        """


class IICMPTransport(Interface):
    """
    Transport for ICMP DatagramProtocols.
    """
    def write(packet, addr=None):
        """
        Write packet to given address.

        @param addr: a tuple of (ip, port). For connected transports must
                     be the address the transport is connected to, or None.
                     In non-connected mode this is mandatory.
        """

    def connect(host, port):
        """
        Connect the transport to an address.

        This changes it to connected mode. Datagrams can only be sent to
        this address, and will only be received from this address. In addition
        the protocol's connectionRefused method might get called if destination
        is not receiving datagrams.

        @param host: an IP address, not a domain name ('127.0.0.1', not 
            'localhost')
        @param port: port to connect to.
        """

    def getHost():
        """
        Returns L{IPv4Address}.
        """

    def stopListening():
        """
        Stop listening on this port.

        If it does not complete immediately, will return L{Deferred} that fires
        upon completion.
        """

