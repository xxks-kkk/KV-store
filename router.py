import config
class Router:
    
    def __init__(self, serverId):
        # neighbours = [0] * SERVER_COUNT
        # neighbours[serverId] = 1
        self.id = serverId
        self.routeMat = [[]] * SERVER_COUNT
        self.routeMat[serverId] = [serverId]

    def receivedPayload(self, payload):
        '''
        return: num of the dests required to forward
        payload: routeMat of the sender
        '''
        sendId = payload[0]
        sendRouteMat = payload[1]
        #Build new connection for forward
        for i in range(SERVER_COUNT):
            if len(self.routeMat[i]) == 0 and sendRouteMat[i]:
                self.routeMat[i] = [sendId] + sendRouteMat[i]
            if self.routeMat[i] and self.routeMat[i][0] == sendId and len(sendRouteMat[i]) == 0:
                self.routeMat[i] = []

    def getPayload(self):
        return (self.id , self.routeMat)

    def nextStop(self, receiveId):
        if len(self.routeMat[receiveId]):
            return self.routeMat[receiveId][0]
        else:
            return SERVER_COUNT

    def neighbourChange(self, serverId, val):
        '''
        it should get from the network layer, here it is used for testing
        assume if it is neighbour, the val is used for discoonected
        if it is not connected, it is used for connect as neighbour
        '''
        # neighbours[serverId] = val
        if val:
            self.routeMat[serverId] = [serverId]
        else:
            self.routeMat[serverId] = []

    if __name__ == '__main__':
        pass


        




