# Purpose: vector clock

def isHappenBefore(c1, c2):
    for i in range(c1.server_num):
        if c1.vector_clock[i] < c2.vector_clock[i]:
            c1.vector_clock[i] = c2.vector_clock[i] 


class Clock:
    # the numbers of server in the system
    server_num = 5
    vector_clock = []
    
    def __init__(self):
        self.vector_clock = [0] * self.server_num

    
    def incrementClock(self, id):
        self.vector_clock[id] += 1


    def onMessageReceived(self, id, c2):
        isHappenBefore(self, c2)
        self.incrementClock(id)

