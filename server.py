# Purpose: only do messaging between server and client
from twisted.web import xmlrpc, server
from twisted.internet.protocol import Protocol, Factory
from twisted.internet.task import LoopingCall
from twisted.internet import endpoints
from twisted.python import log
from model import Model
from clock import Clock
from router import Router
import copy
import config
import json


class ServerProxy(object):
    def __init__(self, serverId):
        self.serverId = int(serverId)
        self.model = Model(self)
        self.timeStamp = Clock()
        self.router = Router(self.serverId) 
        self.lc_call = LoopingCall(self.gossip)

    def greeting(self, protocol, id):
        # setup connection between factory and protocol
        id = int(id)
        protocol.remote_id = id
        protocol.factory.peers[id] = protocol
        protocol.factory.proxy.router.neighbourChange(id, True)

        self.timeStamp.incrementClock(self.serverId)
        protocol.sendData({
            "Method": "Hello",
            "ReceiverId": id,
            "SenderId": self.serverId,
            "TimeStamp": self.timeStamp.vector_clock
        })

    def gossip(self):
        for peer in self.factory.peers.keys():
            self.sendMessage({
                "Method": "Gossip",
                "ReceiverId": peer,
                "Payload": self.router.getPayload()
            })

    def messageReceived(self, message):
        if message["ReceiverId"] != self.serverId:
            self.sendMessage(message)
        senderId = message["SenderId"]
        self.timeStamp.onMessageReceived(self.serverId,
                                         Clock(message["TimeStamp"]))
        if not self.lc_call.running:
            self.lc_call.start(config.GOSSIP_INTERVAL)
        if message["Method"] == "Hello":
            pass
        elif message["Method"] == "Put":
            self.model.put_internal(message["Payload"])
        elif message["Method"] == "Ack":
            msgId = message.get("MessageId", None)
            if not msgId:
                log.err(
                    _stuff=message,
                    _why="No MessageId passed",
                    system=self.tag)
                return
            if msgId in self.model.writeLog:
                log.err(
                    _stuff=message,
                    _why="MessageId not in writeLog",
                    system=self.tag)
                return
            self.model.writeLog[msgId][receiptVector][senderId] = 1
        elif message["Method"] == "Gossip":
            self.router.receivedPayload(message["Payload"])
        else:
            log.err(
                _stuff=message, _why="Unrecognised method", system=self.tag)

    @property
    def tag(self):
        return "Server-{}".format(self.serverId)

    def setFactory(self, factory):
        self.factory = factory

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
        # test if message contains precondition
        self.timeStamp.incrementClock(self.serverId)
        message["TimeStamp"] = self.timeStamp.vector_clock
        message["SenderId"] = self.serverId
        nextStop = self.router.nextStop(message["ReceiverId"])
        if nextStop is None:
            log.err(_stuff=message, _why="Unreachable Node", system=self.tag)
            return False
        self.factory.peers[nextStop].sendData(message)

        # sendMessage


class ServerProtocol(Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.remote_id = None

    def connectionMade(self):
        remote_ip = self.transport.getPeer()
        host_ip = self.transport.getHost()
        self.remote_ip = remote_ip.host + ":" + str(remote_ip.port)
        self.host_ip = host_ip.host + ":" + str(host_ip.port)
        log.msg(
            "Connected from {}".format(remote_ip),
            system=self.factory.proxy.tag)

    def connectionLost(self, reason):
        if self.remote_id in self.factory.peers:
            self.factory.peers.pop(self.remote_id)
        if self.remote_id is not None:
            self.factory.proxy.router.neighbourChange(self.remote_id, False)
        log.msg(
            "Connection lost from {}".format(self.remote_id),
            system=self.factory.proxy.tag)

    def sendData(self, message):
        self.transport.write(json.dumps(message) + "\n")

    def dataReceived(self, data):
        for line in data.splitlines():
            line = line.strip()
            message = json.loads(line)
            if self.remote_id == None:
                self.remote_id = message["SenderId"]
                log.msg(
                    "Connection confirmed from Server[{}]: {}".format(
                        self.remote_id, self.remote_ip),
                    system=self.factory.proxy.tag)
                self.factory.proxy.router.neighbourChange(self.remote_id, True)
                if self.remote_id not in self.factory.peers:
                    self.factory.peers[self.remote_id] = self
          #  log.msg("Received {} from {}.".format(message, self.remote_id))
          #  self.factory.proxy.messageReceived(message)


class ServerFactory(Factory):
    protocol = ServerProtocol

    def __init__(self, proxy):
        # Factory.__init__(self)
        self.peers = {}
        self.proxy = proxy
        proxy.setFactory(self)

    def buildProtocol(self, addr):
        return ServerProtocol(self)


class ServerRPC(xmlrpc.XMLRPC):
    def __init__(self, proxy, **kwargs):
        xmlrpc.XMLRPC.__init__(self, **kwargs)
        self.proxy = proxy
        if str(proxy.serverId) not in config.ADDR_PORT:
            raise Exception("Node not exist")
        _, self.port, kind = config.ADDR_PORT.get(str(proxy.serverId))
        if kind != "server":
            raise Exception("Try to start a server on client port")

    def xmlrpc_createConnection(self, cid):
        host, port, _ = config.ADDR_PORT[str(cid)]
        if cid in self.proxy.factory.peers: return 0
        point = endpoints.TCP4ClientEndpoint(reactor, host, port + 500)
        d = point.connect(self.proxy.factory)
        d.addCallback(self.proxy.greeting, cid)
        return 0

    def xmlrpc_breakConnection(self, cid):
        cid = int(cid)
        if cid in self.proxy.factory.peers:
            peer = self.proxy.factory.peers[cid]
            peer.transport.loseConnection()
        return 0

    def xmlrpc_stabilize(self):
        log.msg("Fake Statbilizing...")
        return 0

    def xmlrpc_printStore(self):
        return self.proxy.model.printStore()

    def xmlrpc_put(self, key, value):
        self.proxy.timeStamp.incrementClock(self.proxy.serverId)
        self.proxy.model.put({
            "key": key,
            "value": value,
            "serverId": self.proxy.serverId,
            "timeStamp": copy.copy(self.proxy.timeStamp).vector_clock
        })
        return self.proxy.timeStamp.vector_clock

    def xmlrpc_get(self, key, cachedTimeStamp):
        return self.proxy.model.get(key, cachedTimeStamp)


if __name__ == '__main__':
    from twisted.internet import reactor
    from optparse import OptionParser
    parser = OptionParser(
        usage="The storage server instance, should be called by watchdog.")
    parser.add_option(
        "-i",
        "--serverId",
        metavar="PORT_NUM",
        type="string",
        dest="serverId",
        help="server id")
    (options, args) = parser.parse_args()
    log.startLogging(config.LOG_FILE)
    host, listenPort, _ = config.ADDR_PORT[options.serverId]
    proxy = ServerProxy(options.serverId)
    serverEndpoint = endpoints.TCP4ServerEndpoint(reactor, listenPort + 500)
    factory = ServerFactory(proxy)
    serverEndpoint.listen(factory)
    # for i, (IP, port, kind) in config.ADDR_PORT.items():
    #     if kind != "server" or int(i) >= int(options.serverId): continue
    #     point = endpoints.TCP4ClientEndpoint(reactor, host, port + 500)
    #     d = point.connect(factory)
    #     d.addCallback(proxy.greeting, int(i))

    s = ServerRPC(proxy)
    rpcEndpoint = endpoints.TCP4ServerEndpoint(reactor, listenPort)
    rpcEndpoint.listen(server.Site(s))
    log.msg("Server Running on {}.".format(s.port))
    reactor.run()
