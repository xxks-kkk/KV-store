from SimpleXMLRPCServer import SimpleXMLRPCServer
import xmlrpclib
import argparse
import config
import sys
import os
import time
import pickle

joinSeq = [False] * config.SERVER_COUNT
kv_store = {}

def joinServer(dogs, clients, servers, arg):
    dogs[int(arg[1])].joinServer(int(arg[1]), joinSeq)
    joinSeq[int(arg[1])] = True

def killServer(dogs, clients, servers, arg):
    dogs[int(arg[1])].killServer()
    joinSeq[int(arg[1])] = False

def joinClient(dogs, clients, servers, arg):
    clients[int(arg[1]) % config.CLIENT_COUNT].joinClient(int(arg[2]))

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

def stabilize(dogs, clients, servers, arg):
    time.sleep(5)
    # for server in servers:
    #     server.stabilize()

def printStore(dogs, clients, servers, arg):
    disKvStore = servers[int(arg[1])].printStore()
    if debug:
        for keys in kv_store:
            if keys not in disKvStore or disKvStore[key] != kv_store[keys]:
                print('the key %s has a wrong value' % (keys))
                return 
    print servers[int(arg[1])].printStore()

def put(dogs, clients, servers, arg):
    # what happens if there are ' ' in key and value
    clients[int(arg[1]) % config.CLIENT_COUNT].put(arg[2], arg[3])

def get(dogs, clients, servers, arg):
    res = clients[int(arg[1]) % config.CLIENT_COUNT].get(arg[2]) 
    print "get {} = {}".format(arg[2], res)

if __name__ == "__main__":
    # 1. connect with five server watchdogs and five clients and five servers
    #    (NOTE: connect with watchdogs before servers)
    # 2. Wait for the Samantha's command
    os.system("rm -rf dict")
    dogs, clients, servers = [], [], []
    for i in range(config.SERVER_COUNT):
        dogs.append( xmlrpclib.ServerProxy('http://' + str(config.WATCHDOG_IP_LIST[i]) + ':' + str(config.WATCHDOG_PORT[i])))
        clients.append(xmlrpclib.ServerProxy('http://' + str(config.CLIENT_IP_LIST[i])+ ':' + str(config.CLIENT_PORT[i])))
        servers.append(xmlrpclib.ServerProxy('http://' + str(config.WATCHDOG_IP_LIST[i]) + ':' +str(config.SERVER_PORT[i])))

    command2func = {
                    'joinServer' : joinServer,
                    'killServer' : killServer,
                    'joinClient' : joinClient,
                    'breakConnection' : breakConnection,
                    'createConnection' : createConnection,
                    'stabilize' : stabilize,
                    'printStore' : printStore,
                    'put' : put,
                    'get' : get
    }

    start = time.time()
    commandCount = 0

    kv_store = pickle.load(open('commandConnected_40' ,'r'))

    while True:
        input = sys.stdin.readline().strip('\n')
        commandCount += 1
        if len(input) == 0 or input.startswith("#"):
            break
        print input
        arg = input.split(' ')
        func = command2func.get(arg[0], None)
        if func:
            func(dogs, clients, servers, arg)
            if debug and arg[0] == 'put':
                kv_store[arg[2]] = arg[3]
        else:
            continue

    allTime = time.time() - start
    print('throughput is %f requests per second',commandCount / allTime)

