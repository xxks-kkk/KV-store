from SimpleXMLRPCServer import SimpleXMLRPCServer
import xmlrpclib
import argparse
import config
import sys
import os
import time
import errno
import socket
import pickle


joinSeq = [False] * config.SERVER_COUNT
kv_store = {}

def joinServer(dogs, clients, servers, arg):
    server_id = int(arg[1])
    dogs[server_id].joinServer(server_id, joinSeq)
    i = 0
    while True:
        time.sleep(config.CHECK_INTERVAL)
        i += config.CHECK_INTERVAL
        try:
            if servers[server_id].hello() == 0:
                break
        except socket.error as err:
            if err.errno != errno.ECONNREFUSED:
                raise err
    if config.DEBUG:
        print "Server[{}] joined in {} seconds.".format(server_id, i)
    joinSeq[server_id] = True

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
        i = 0
        while servers[id2].isConnectedTo(id1):
            time.sleep(config.CHECK_INTERVAL)
            i += config.CHECK_INTERVAL
        if config.DEBUG:
            print "Connection betwen Server[{}] Server[{}] break in {} seconds.".format(id1, id2, i)
    else:
        clients[max(id1, id2) % config.CLIENT_COUNT].breakConnection(min(id1, id2))

def createConnection(dogs, clients, servers, arg):
    id1, id2 = int(arg[1]), int(arg[2])
    if id1 < config.SERVER_COUNT and id2 < config.SERVER_COUNT:
        servers[id1].createConnection(id2)
    else:
        clients[max(id1, id2) % config.CLIENT_COUNT].createConnection(min(id1, id2))

def stabilize(dogs, clients, servers, arg):
    i = 0
    while True:
        finished = True
        for j, server in enumerate(servers):
            if joinSeq[j] and not server.status(joinSeq):
                finished = False
                break
        if finished:
            break
        time.sleep(config.STABILIZE_INTERVAL)
        i += config.STABILIZE_INTERVAL
    if config.DEBUG:
        print("stabilized after {} second.".format(i))

def printStore(dogs, clients, servers, arg):
    global kv_store
    disKvStore = servers[int(arg[1])].printStore()
    if config.DEBUG:
        if int(arg[1]) == 0:
            kv_store = disKvStore
        else:
            for key in kv_store:
                if key not in disKvStore or disKvStore[key] != kv_store[key]:
                    print('On the server %s the key %s has a wrong value' % (arg[1], key))
                    print("Remote Value: {}".format(disKvStore[key][0:20] if key in disKvStore else None) )
                    print("Ground Truth: {}".format(kv_store[key][0:20]))
    if config.DISPLAY_COMMAND:
        for k, v in disKvStore.items():
            print "{}:{}".format(k, v)
    # print servers[int(arg[1])].printStore()

def put(dogs, clients, servers, arg):
    # what happens if there are ' ' in key and value
    clients[int(arg[1]) % config.CLIENT_COUNT].put(arg[2], arg[3])

def get(dogs, clients, servers, arg):
    res = clients[int(arg[1]) % config.CLIENT_COUNT].get(arg[2]) 
    print res

if __name__ == "__main__":
    # 1. connect with five server watchdogs and five clients and five servers
    #    (NOTE: connect with watchdogs before servers)
    # 2. Wait for the Samantha's command
    os.system("rm -rf dict log")
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


    while True:
        input = sys.stdin.readline().strip('\n')
        commandCount += 1
        if len(input) == 0 or input.startswith("#"):
            break
        if config.DEBUG:
            if config.DISPLAY_COMMAND:
                print "excecuting command [{}]: {}".format(commandCount, input[:30])
            else:
                print "excecuting command [{}]".format(commandCount)
        arg = input.split(' ')
        func = command2func.get(arg[0], None)
        if func:
            func(dogs, clients, servers, arg)
        else:
            continue

    allTime = time.time() - start
    print allTime
    print('throughput is %f requests per second' % (commandCount / allTime))

