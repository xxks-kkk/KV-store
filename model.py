# Purpose: logic layer on top of server
# (handling put/get requests)

from twisted.python import log
import uuid
import file_dict
import config
import clock

class Model:
    RECEIPT_IDX = 3
    """
    [
    "UUID": ["key", "value", "timeStamp", "serverId", "receiptVector"],
    "UUID": ["key", "value", "timeStamp", "serverId", "receiptVector"],
    ]
    """
    def __init__(self, serverProxy):
        self.serverProxy = serverProxy
        self.writeLog = {}
        self.successLog = {}
        self.receiptVector = [0] * config.NUM_SERVER
        self.receiptVector[self.serverProxy.serverId] = 1
        self.fileDict = file_dict.FileDictionary(serverProxy.serverId)

    def printStore(self): # return the dictionary content to a string
        content = ""
        for key in self.fileDict.data.keys():
            content +=  str(key) + ":" + str(self.fileDict.data[key]['value']) + "\n"
        return content

    def put_internal(self, item):
        """
        Put request comes from peer servers
        :param item: a dictionary with "key", "value", "serverId", "timeStamp"
        :return:
        """
        key = item['key']
        value = item['value']
        timeStamp = item['timeStamp']
        serverId = item['serverId']
        messageId = item['messageId']
        if key not in self.fileDict or clock.isHappenBefore(self.serverProxy.serverId,
                                                         clock.Clock(self.fileDict[key]['timeStamp']),
                                                         serverId,
                                                         clock.Clock(timeStamp)):
            # Our server doesn't have this KV pair or our KV pair is outdated
            self.fileDict.put(item)
        self.serverProxy.sendMessage({"ReceiverId": serverId,
                                     "MessageId": messageId,
                                     "Method": "Ack",
                                     "Payload": messageId})

    def ack(self, message):
        msgId = message.get("MessageId", None)
        payload = message.get("Payload")
        if not msgId:
            log.err(
                _stuff=message,
                _why="No MessageId passed",
                system=self.serverProxy.tag)
            return
        if msgId in self.successLog:
            return
        if msgId in self.writeLog:
            log.err(
                _stuff=message,
                _why="MessageId not in writeLog",
                system=self.serverProxy.tag)
            return
        item = self.writeLog[msgId]
        item[self.RECEIPT_IDX][int(payload["serverId"])] = 1
        if sum(item[self.RECEIPT_IDX]) == 5:
            self.successLog[msgId] = item
            del self.writeLog[msgId]

    def put(self, item):
        """
        Put request from client that is passed from the server module
        :param item: a dictionary with "key", "value", "serverId", "timeStamp", "messageId"
        :return:
        """
        id = str(uuid.uuid1())
        item['messageId'] = id
        self.fileDict.put(item)
        self.writeLog[id] = ["put", item, list(self.receiptVector)]
        for i in range(config.NUM_SERVER):
            if i != self.serverProxy.serverId:
                self.serverProxy.sendMessage({"ReceiverId": i, "MessageId": id, "Method": "Put", "Payload": item})
                # "Payload" means the content send to the network

    def get(self, key, timeStamp):
        """
        return according to API specification.
        """
        print "comparing self {} and client {}".format(self.serverProxy.timeStamp.vector_clock, timeStamp)
        if timeStamp is None or clock.isHappenBefore(0, clock.Clock(timeStamp), 0, self.serverProxy.timeStamp):
            try:
                return self.fileDict.data[key]['value']
            except KeyError:
                return config.KEY_ERROR if timeStamp is None else config.ERR_DEP
        else:
            return config.ERR_DEP

    def dump(self):
        self.fileDict.dump()

    def resend(self):
        # We want to constant check our writeLog and resend the message
        # to the server that hasn't ack our message
        for messageId in self.writeLog:
            for server_id in range(config.NUM_SERVER):
                if self.writeLog[messageId][2][server_id] == 1:
                    # our ACK status vector is at 2nd position (0-index) of the list
                    pass
                else:
                    self.serverProxy.sendMessage({"ReceiverId": server_id, "MessageId": messageId, "Method": "Put", "Payload": self.writeLog[messageId][1]})

if __name__ == "__main__":
    pass
