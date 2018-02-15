# Purpose: only do messaging between server and client
from twisted.web import xmlrpc, server
from twisted.python import log
import config


class ServerProxy():
    timeStamp = None
    def __init__(self, serverId):
        pass

    def onMessageReceived(self):
        pass

    def sendMessage(self, message):
        """
        precondition{
        "receiverId":,
        "messageId":,
        "Method":,
        "Payload":, 
        }
        this method adds "senderId" and "timeStamp".
        """
        pass


class Server(xmlrpc.XMLRPC):

    def __init__(self, serverId, **kwargs):
        xmlrpc.XMLRPC.__init__(self, **kwargs)
        if serverId not in config.ADDR_PORT:
            raise Exception("Node not exist")
        _, self.port, kind = config.ADDR_PORT.get(serverId)
        if kind != "server":
            raise Exception("Try to start a server on client port")

    def xmlrpc_stabilize(self):
        log.msg("Fake Statbilizing...")
        return 0

    def xmlrpc_printStore(self):
        log.msg("Fake printStore...")
        return 0


if __name__ == '__main__':
    from twisted.internet import reactor, endpoints
    from optparse import OptionParser
    parser = OptionParser(
        usage="The storage server instance, should be called by watchdog.")
    parser.add_option(
        "-i",
        "--serverId",
        metavar="PORT_NUM",
        type="string",
        dest="id",
        help="server id")
    (options, args) = parser.parse_args()
    log.startLogging(config.LOG_FILE)
    s = Server(serverId=options.id)
    endpoint = endpoints.TCP4ServerEndpoint(reactor, s.port)
    endpoint.listen(server.Site(s))
    log.msg("Server Running on {}.".format(s.port))
    reactor.run()
