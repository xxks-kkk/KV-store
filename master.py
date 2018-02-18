from SimpleXMLRPCServer import SimpleXMLRPCServer
import argparse
import config

joinSeq = [False] * config.SERVER_COUNT

def joinServer(dogs, clients, servers, arg):
    dogs[int(arg[1])].joinServer()
    for i in range(config.SERVER_COUNT):
        if joinSeq[i]:
            createConnection(dogs, clients, servers, (0, arg[1], i))
    joinSeq[int(arg[1])] = True

def killServer(dogs, clients, servers, arg):
    dogs[int(arg[1])].killServer()
    joinSeq[int(arg[1])] = False

def joinClient(dogs, clients, servers, arg):
    clients[int(arg[1]) % config.CLIENT_COUNT].joinServer(int(arg[2]))
    pass

def breakConnection(dogs, clients, servers, arg):
    # if break between client and server, send to client, 
    # elseif between 2 servers, send to first server to execute
    id1, id2 = int(arg[1]), int(arg[2])
    if id1 < config.SERVER_COUNT and id2 < config.SERVER_COUNT:
        servers[id1].breakConnection(id2)
    else:
        clients[max(id1, id2) % config.CLIENT_COUNT].breakConnection(min(id1, id2))

def createConnection(dogs, clients, servers, arg):
    id1, id2 = int(arg[1]), int(arg[2])
    if id1 < config.SERVER_COUNT and id2 < config.SERVER_COUNT:
        servers[id1].createConnection(id2)
    else:
        clients[max(id1, id2) % config.CLIENT_COUNT].createConnection(min(id1, id2))

def stablize(dogs, clients, servers, arg):
    for server in servers:
        server.stablize()

def printStore(dogs, clients, servers, arg):
    servers[int(arg[1])].printStore()

def put(dogs, clients, servers, arg):
    # what happens if there are ' ' in key and value
    clients[int(arg[1]) % config.CLIENT_COUNT].put(arg[2], arg[3])

def get(dogs, clients, servers, arg):
    clients[int(arg[1]) % config.CLIENT_COUNT].get(arg[2])

if __name__ == "__main__":
    # 1. connect with five server watchdogs and five clients and five servers
    #    (NOTE: connect with watchdogs before servers)
    # 2. Wait for the Samantha's command
    dogs, clients, servers = [], [], []
    for i in range(config.SERVER_COUNT):
        dogs.append( xmlrpclib.ServerProxy('http://' + config.WATCHDOG_IP_LIST[i] + ':' + config.WATCHDOG_PORT[i]))
        clients.append(xmlrpclib.ServerProxy('http://' + config.CLIENT_IP_LIST[i]+ ':' + config.CLIENT_PORT[i]))
        servers.append(xmlrpclib.ServerProxy('http://' + config.WATCHDOG_IP_LIST[i] + ':' + config.SERVER_PORT[i]))

    command2func = {
                    'joinServer' : joinServer,
                    'killServer' : killServer,
                    'joinClient' : joinClient,
                    'breakConnection' : breakConnection,
                    'createConnection' : createConnection,
                    'stablize' : stablize,
                    'printStore' : printStore,
                    'put' : put,
                    'get' : get
    }

    try:
        while True:
            input = sys.stdin.readline().strip('\n')
            arg = input.split(' ')
            func = command2func.get(arg[0], 'nothing')
            func(dogs, clients, servers, arg)
    except:
        pass
