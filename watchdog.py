# Purpose: fire up server, talk with master
# implemented as RPC server
from twisted.web import xmlrpc
from twisted.python import log
import subprocess
import config


class WatchDogServer(xmlrpc.XMLRPC):
    proc = None

    def __init__(self, port, **kwargs):
        xmlrpc.XMLRPC.__init__(self, **kwargs)
        self.port = port

    def xmlrpc_joinServer(self, id):
        if self.proc is not None:
            print "Fault"
            return xmlrpc.Fault(1, "Server already started.")
        try:
            self.proc = subprocess.Popen(["python", "server.py", "-i", str(id)])
            return 0
        except Exception as e:
            return xmlrpc.Fault(2, str(e))

    def xmlrpc_killServer(self):
        if self.proc is None:
            return xmlrpc.Fault(1, "Server hasn't started.")
        try:
            self.proc.kill()
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
