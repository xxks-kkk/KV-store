# Purpose: only do messaging between server and client
from twisted.web import xmlrpc, server
from twisted.internet.protocol import Protocol, Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet.task import LoopingCall
from twisted.internet import endpoints
from twisted.python import log
from model import Model
from clock import Clock
from router import Router
import config
import json
import traceback


class ServerProxy(object):
    def __init__(self, serverId):
        self.serverId = int(serverId)
        self.model = Model(self)
        self.timeStamp = Clock(serverId=self.serverId)
        self.router = Router(self.serverId)

        self.lc_gossip = LoopingCall(self.gossip)
        self.lc_resend = LoopingCall(self.model.resend)

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
        self.timeStamp.onMessageReceived(self.serverId,
                                         Clock(message["TimeStamp"]))
        if message["ReceiverId"] != self.serverId:
            self.sendMessage(message)
            return
        senderId = message["SenderId"]
        if not self.lc_gossip.running:
            self.lc_gossip.start(config.GOSSIP_INTERVAL)
        if not self.lc_resend.running:
            self.lc_resend.start(config.RESEND_INTERVAL)
        # if message["Method"] != "Gossip":
        #     log.msg("Message Received: {}".format(message))

        if message["Method"] == "Hello":
            pass
        elif message["Method"] == "Put":
            self.model.put_internal(message["Payload"])
        elif message["Method"] == "Ack":
            self.model.ack(message)
        elif message["Method"] == "Gossip":
            self.router.receivedPayload(message["Payload"])
        else:
            log.msg("Unrecognised method: {}".format(message), system=self.tag)

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
        message["TimeStamp"] = list(self.timeStamp.vector_clock)
        if "SenderId" not in message:
            message["SenderId"] = self.serverId
        nextStop = self.router.nextStop(message["ReceiverId"])
        if nextStop is None:
            return False
        try:
            self.factory.peers[nextStop].sendData(message)
        except KeyError:
            log.msg(
                "KeyError(trying to send to {}): {}".format(nextStop, message),
                system=self.tag)
            self.router.showRouters()

        # sendMessage

    def onShutDown(self):
        # When we receive SIGINT, we save the data from the memory to disk
        self.model.dump()
        self.timeStamp.dump()


class ServerProtocol(LineReceiver):
    def __init__(self, factory):
        self.factory = factory
        self.remote_id = None
        self.setLineMode()

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
        self.sendLine(json.dumps(message))

    def lineReceived(self, line):
        line = line.strip()
        try:
            message = json.loads(line)
        except ValueError as e:
            print(e)
            print(line)
            raise e
        if self.remote_id == None:
            self.remote_id = message["SenderId"]
            log.msg(
                "Connection confirmed from Server[{}]: {}".format(
                    self.remote_id, self.remote_ip),
                system=self.factory.proxy.tag)
            self.factory.proxy.router.neighbourChange(self.remote_id, True)
            if self.remote_id not in self.factory.peers:
                self.factory.peers[self.remote_id] = self
        self.factory.proxy.messageReceived(message)



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
        self.proxy.timeStamp.incrementClock(self.proxy.serverId)
        host, port, _ = config.ADDR_PORT[str(cid)]
        if cid in self.proxy.factory.peers: return 0
        point = endpoints.TCP4ClientEndpoint(reactor, host, port + 500)
        d = point.connect(self.proxy.factory)
        d.addCallback(self.proxy.greeting, cid)
        return 0

    def xmlrpc_breakConnection(self, cid):
        self.proxy.timeStamp.incrementClock(self.proxy.serverId)
        cid = int(cid)
        if cid in self.proxy.factory.peers:
            peer = self.proxy.factory.peers[cid]
            peer.transport.loseConnection()
        else:
            log.msg(
                "Connection haven't established with server {}".format(cid),
                self.proxy.tag)
        return 0

    def xmlrpc_isConnectedTo(self, serverId):
        status = serverId in self.proxy.factory.peers
        return status

    def xmlrpc_status(self, on_machines):
        return self.proxy.model.status(on_machines)

    def xmlrpc_printStore(self):
        self.proxy.timeStamp.incrementClock(self.proxy.serverId)
        return self.proxy.model.printStore()

    def xmlrpc_put(self, key, value):
        self.proxy.timeStamp.incrementClock(self.proxy.serverId)
        # the function may get interrupted and self.proxy.timeStamp.vector_clock
        # may get updated by other functions (since by reference). Then, we
        # need to make a copy and save the value at the state.
        snapshot = list(self.proxy.timeStamp.vector_clock)
        self.proxy.model.put({
            "key": key,
            "value": value,
            "serverId": self.proxy.serverId,
            "timeStamp": snapshot
        })
        return snapshot

    def xmlrpc_get(self, key, cachedTimeStamp):
        return self.proxy.model.get(key, cachedTimeStamp)

    def xmlrpc_hello(self):
        # dummy rpc to test the liveliness of server
        return 0


if __name__ == '__main__':
    from twisted.internet import reactor
    from optparse import OptionParser
    parser = OptionParser(
        usage="The storage server instance, should be called by watchdog.")
    parser.add_option(
        "-i",
        "--serverId",
        metavar="SERVERID",
        type="string",
        dest="serverId",
        help="server id")
    parser.add_option(
        "-c",
        "--connection",
        metavar="CONNECT_SERVER_ID",
        type="string",
        dest="toConnect",
        nargs=5,
        help="server ids this server to connect to")
    (options, args) = parser.parse_args()
    log.startLogging(open("server_log/{}.log".format(options.serverId), 'w'))
    # log.startLogging(config.LOG_FILE)
    host, listenPort, _ = config.ADDR_PORT[options.serverId]
    proxy = ServerProxy(options.serverId)
    serverEndpoint = endpoints.TCP4ServerEndpoint(reactor, listenPort + 500)
    factory = ServerFactory(proxy)
    serverEndpoint.listen(factory)
    s = ServerRPC(proxy)
    rpcEndpoint = endpoints.TCP4ServerEndpoint(reactor, listenPort)
    rpcEndpoint.listen(server.Site(s))
    if options.toConnect:
        for cid, v in enumerate(options.toConnect):
            if v == "False": continue
            host, port, _ = config.ADDR_PORT[str(cid)]
            point = endpoints.TCP4ClientEndpoint(reactor, host, port + 500)
            d = point.connect(proxy.factory)
            d.addCallback(proxy.greeting, cid)

    log.msg("Server Running on {}.".format(s.port))
    reactor.addSystemEventTrigger('before', 'shutdown', proxy.onShutDown)
    reactor.run()
