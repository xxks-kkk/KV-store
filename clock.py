# Purpose: vector clock


def isHappenBefore(serverId1, c1, serverId2, c2):
    if all([i <= j for i, j in zip(c1.vector_clock, c2.vector_clock)]):
        return True
    elif all([i >= j for i, j in zip(c1.vector_clock, c2.vector_clock)]):
        return False
    else:
        return serverId1 < serverId2


class Clock:
    # the numbers of server in the system
    server_num = 5
    vector_clock = []

    def __init__(self):
        self.vector_clock = [0] * self.server_num

    def incrementClock(self, id):
        self.vector_clock[id] += 1

    def onMessageReceived(self, id, c1):
        for i in range(self.server_num):
            self.vector_clock[i] = max(self.vector_clock[i],
                                       c1.vector_clock[i])
        self.vector_clock[id] += 1
