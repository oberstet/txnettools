from zope.interface import implements

from twisted.internet.selectreactor import SelectReactor

from txnet import icmp
from txnet.interfaces import IReactorICMP


class ExtendedSelectReactor(SelectReactor):

    implements(IReactorICMP)

    def listenICMP(self, port, protocol, interface="", maxPacketSize=8192):
        """
        Connects a given DatagramProtocol to the given numeric ICMP port.

        @return: obect which provides L{IListeningPort}.

        """
        p = icmp.Port(port, protocol, interface, maxPacketSize, self)
        p.startListening()
        return p


def install():
    """
    Configure the twisted mainloop to be run using the select() reactor via the
    ExtendedSelectReactor.
    """
    reactor = ExtendedSelectReactor()
    from twisted.internet.main import installReactor
    installReactor(reactor)
    return reactor


reactor = install()
