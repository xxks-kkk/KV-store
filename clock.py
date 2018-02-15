# Purpose: vector clock

import config

def isHappenBefore(serverId1, c1, serverId2, c2):
    # c2 is sender and c1 is receiver
    for i in range(c1.server_num):
        if c1.vector_clock[i] < c2.vector_clock[i]:
            c1.vector_clock[i] = c2.vector_clock[i] 


class Clock:
    # the numbers of server in the system
    server_num = config.NUM_SERVER
    vector_clock = []
    
    def __init__(self):
        self.vector_clock = [0] * self.server_num

    
    def incrementClock(self, id):
        self.vector_clock[id] += 1


    def onMessageReceived(self, id, c2):
        isHappenBefore(self, c2)
        self.incrementClock(id)

