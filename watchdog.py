# Purpose: fire up server, talk with master
# implemented as RPC server
from twisted.web import xmlrpc
from twisted.internet import defer
from twisted.python import log
import subprocess
import config


class WatchDogServer(xmlrpc.XMLRPC):
    proc = None

    def __init__(self, port, **kwargs):
        xmlrpc.XMLRPC.__init__(self, **kwargs)
        self.port = port

    def xmlrpc_joinServer(self, id, toConnect=None):
        if self.proc is not None:
            return xmlrpc.Fault(1, "Server already started.")
        try:
            command = ["python", "server.py", "-i", str(id)]
            if toConnect:
                command += list(map(str, toConnect))
            self.proc = subprocess.Popen(command)
            d = defer.Deferred()
            from twisted.internet import reactor
            reactor.callLater(0.5, d.callback, None)
            d.addCallback(lambda _: 0)
            return d
        except Exception as e:
            return xmlrpc.Fault(2, str(e))

    def xmlrpc_killServer(self):
        if self.proc is None:
            return xmlrpc.Fault(1, "Server hasn't started.")
        try:
            # send a SIGTERM to self.proc and wait for it to terminate
            self.proc.terminate()
            self.proc.wait()
            self.proc = None
            return 0
        except Exception as e:
            return xmlrpc.Fault(2, str(e))


if __name__ == '__main__':
    from twisted.internet import reactor
    from twisted.web import server
    from optparse import OptionParser
    parser = OptionParser(
        usage="Serverside watchdog for receiving master program instructions.")
    parser.add_option(
        "-p",
        "--port",
        metavar="PORT_NUM",
        default=config.WATCHDOG_PORT,
        type="int",
        dest="port",
        help="the port watchdog will listen to.")
    (options, args) = parser.parse_args()
    log.startLogging(config.LOG_FILE)
    watchdog = WatchDogServer(options.port)
    reactor.listenTCP(watchdog.port, server.Site(watchdog))
    log.msg("WatchDog Server Running on {}.".format(watchdog.port))
    reactor.run()
