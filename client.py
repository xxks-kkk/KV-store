from twisted.web import xmlrpc, server
from twisted.python import log
import subprocess
import config
log.startLogging(config.LOG_FILE)


class ClientProxy:
    """
    The proxy of connecting to kv-store server
    """

    def __init__(self):
        self.fakedict = {}
        pass

    def connect(self, serverId):
        log.msg("[Fake Dict]Connnected to Server_{}.".format(serverId))

    def disconnect(self):
        log.msg("[Fake Dict]disconnect from Server_{}.".format(serverId))

    def put(self, key, value):
        self.fakedict[key] = value
        return 0

    def get(self, key):
        return self.fakedict.get(key, None)


class ClientServer(xmlrpc.XMLRPC):
    """
    It's actually a xmlrpc server for accepting master scripts' procedure calls
    """

    def __init__(self, **kwargs):
        xmlrpc.XMLRPC.__init__(self, **kwargs)
        self.port = config.CLIENT_PORT
        self.proxy = ClientProxy()

    def xmlrpc_joinClient(self, serverId):
        log.msg("joinClient Called!")
        # RPC server implementation
        # for master
        try:
            self.proxy.connect(serverId)
            return 0
        except Exception as e:
            return xmlrpc.Fault(1, str(e))

    def xmlrpc_breakConnection(self, serverId):
        try:
            self.proxy.disconnect()
            return 0
        except Exception as e:
            return xmlrpc.Fault(1, str(e))

    def xmlrpc_get(self, key):
        # RPC server implementation
        # for master; RPC client implementation
        # for server
        return self.proxy.get(key)

    def xmlrpc_put(self, key, value):
        return self.proxy.put(key, value)

if __name__ == "__main__":
    from twisted.internet import reactor, endpoints
    client = ClientServer()
    endpoint = endpoints.TCP4ServerEndpoint(reactor, client.port)
    endpoint.listen(server.Site(client))
    log.msg("Client Running on {}.".format(client.port))
    reactor.run()
