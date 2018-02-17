import config
import random

class Router:
    def __init__(self, serverId):
        # neighbours = [0] * SERVER_COUNT
        # neighbours[serverId] = 1
        self.id = serverId
        self.routeMat = [[]] * config.SERVER_COUNT
        self.routeMat[serverId] = [serverId]

    def receivedPayload(self, payload):
        '''
        return: num of the dests required to forward
        payload: routeMat of the sender
        '''
        sendId = payload[0]
        sendRouteMat = payload[1]
        isChange = False
        #Build new connection for forward
        for i in range(config.SERVER_COUNT):
            if len(self.routeMat[i]) == 0 and sendRouteMat[i]:
                self.routeMat[i] = [sendId] + sendRouteMat[i]
                isChange = True
            if self.routeMat[i] and self.routeMat[i][0] == sendId and len(sendRouteMat[i]) == 0:
                self.routeMat[i] = []
                isChange = True
        return isChange

    def getPayload(self):
        return (self.id , self.routeMat)

    def nextStop(self, receiveId):
        if len(self.routeMat[receiveId]):
            return self.routeMat[receiveId][0]
        else:
            return False

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

    def showRouters(self):
        print self.routeMat

if __name__ == '__main__':
    routers = []
    # all are neighbours at first
    for i in range(config.SERVER_COUNT):
        routers.append(Router(i))
        for j in range(config.SERVER_COUNT):
            routers[i].neighbourChange(j, True)

    # 0 3  ==> break
    routers[0].neighbourChange(3, False)
    routers[3].neighbourChange(0, False)
    routers[2].neighbourChange(3, False)
    routers[3].neighbourChange(2, False)
    routers[1].neighbourChange(3, False)
    routers[3].neighbourChange(1, False)

    routers[0].showRouters()
    routers[0].receivedPayload(routers[2].getPayload())
    routers[3].receivedPayload(routers[4].getPayload())

    #

    routers[0].showRouters()
    routers[3].showRouters()



        




