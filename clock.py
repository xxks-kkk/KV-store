# Purpose: vector clock

import config
import os
import json


def isHappenBefore(serverId1, c1, serverId2, c2):
    # c2 is sender and c1 is receiver
    if all([i <= j for i, j in zip(c1.vector_clock, c2.vector_clock)]):
        return True
    elif all([i >= j for i, j in zip(c1.vector_clock, c2.vector_clock)]):
        return False
    else:
        return serverId1 < serverId2


class Clock:
    # the numbers of server in the system
    vector_clock = []

    def __init__(self, vc=None, serverId=None):
        self.clock_file = os.path.join("log", "clock{}.json".format(serverId))
        if serverId is not None:
            if os.path.exists(self.clock_file):
                with open(self.clock_file, 'r') as f:
                    vc = json.load(f)
        if vc:
            self.vector_clock = list(vc)
        else:
            self.vector_clock = [0] * config.NUM_SERVER

    def dump(self):
        with open(self.clock_file, "w") as f:
            json.dump(self.vector_clock, f)

    def incrementClock(self, id):
        self.vector_clock[id] += 1

    def onMessageReceived(self, id, c1):
        for i in range(config.NUM_SERVER):
            self.vector_clock[i] = max(self.vector_clock[i],
                                       c1.vector_clock[i])
        self.vector_clock[id] += 1
