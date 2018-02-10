# Purpose: fire up server, talk with master
# implemented as RPC server
from twisted.web import xmlrpc
from twisted.python import log
import subprocess
import config
log.startLogging(config.LOG_FILE)


class WatchDogServer(xmlrpc.XMLRPC):
    proc = None

    def xmlrpc_joinServer(self):
        if self.proc is not None:
            return xmlrpc.Fault(1, "Server already started.")
        try:
            self.proc = subprocess.Popen(["python2", "server.py"])
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
    watchdog = WatchDogServer()
    port = config.WATCHDOG_PORT
    reactor.listenTCP(port, server.Site(watchdog))
    log.msg("WatchDog Server Running on {}.".format(port))
    reactor.run()
