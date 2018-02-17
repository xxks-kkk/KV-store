# Purpose: vector clock
from config import NUM_SERVER

def isHappenBefore(serverId1, c1, serverId2, c2):
    # c2 is sender and c1 is receiver
    for i in range(NUM_SERVER):
        if c1.vector_clock[i] < c2.vector_clock[i]:
            c1.vector_clock[i] = c2.vector_clock[i]
    if all([i <= j for i, j in zip(c1.vector_clock, c2.vector_clock)]):
        return True
    elif all([i >= j for i, j in zip(c1.vector_clock, c2.vector_clock)]):
        return False
    else:
        return serverId1 < serverId2


class Clock:
    # the numbers of server in the system
    vector_clock = []

    def __init__(self):
        self.vector_clock = [0] * NUM_SERVER

    def incrementClock(self, id):
        self.vector_clock[id] += 1

    def onMessageReceived(self, id, c1):
        for i in range(NUM_SERVER):
            self.vector_clock[i] = max(self.vector_clock[i],
                                       c1.vector_clock[i])
        self.vector_clock[id] += 1
