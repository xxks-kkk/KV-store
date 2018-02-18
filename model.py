# Purpose: logic layer on top of server
# (handling put/get requests)

from twisted.python import log
import uuid
import file_dict
import config
import clock

class Model:
    """
    [
    "UUID": ["key", "value", "timeStamp", "serverId", "receiptVector"],
    "UUID": ["key", "value", "timeStamp", "serverId", "receiptVector"],
    ]
    """
    def __init__(self, serverProxy):
        self.serverProxy = serverProxy
        self.writeLog = {}
        self.failLog = {}
        self.fileDict = file_dict.FileDictionary(serverProxy.serverId)

    # def onStablize(self):
    #     pass

    def onPrintStore(self):
        # return the dictionary content to a string
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
        if serverId == self.serverProxy.serverId:
            # our server is the destination of the incoming internal put request
            if key in self.fileDict and clock.isHappenBefore(self.serverProxy.serverId,
                                                             self.fileDict[key]['timeStamp'],
                                                             serverId,
                                                             timeStamp):
                # Our server kV pair is the latest. We do nothing and immediately send back the ACK
                self.serverProxy.sendMessage({"receiverId": self.serverProxy.serverId,
                                              "messageId": messageId,
                                              "Method": "Ack",
                                              "Payload": messageId})
            else:
                # Our server doesn't have this KV pair or our KV pair is outdated
                self.fileDict.put(item)
                self.serverProxy.sendMessage({"receiverId": self.serverProxy.serverId,
                                             "messageId": messageId,
                                             "Method": "Ack",
                                             "Payload": messageId})
        else:
            # Our server is the not the target of the internal put request. We use underlying server module to redirect
            # the message to the target server
            self.serverProxy.sendMessage({"receiverId": serverId, "messageId": messageId, "Method": "Put", "Payload": item})


    def put(self, item):
        """
        Put request from client that is passed from the server module
        :param item: a dictionary with "key", "value", "serverId", "timeStamp", "messageId"
        :return:
        """
        id = uuid.uuid1()
        item['messageId'] = id
        self.fileDict.put(item)
        self.writeLog[id] = ["put", item, [0]*config.NUM_SERVER]
        for i in range(config.NUM_SERVER):
            if i == self.serverProxy.serverId:
                continue
            else:
                self.serverProxy.sendMessage({"receiverId": i, "messageId": id, "Method": "Put", "Payload": item})
                # "Payload" means the content send to the network

    def get(self, key, timeStamp):
        """
        return according to API specification.
        """
        if not clock.isHappenBefore(0, self.serverProxy.timeStamp, 0, timeStamp):
            try:
                return self.fileDict.data[key]['value'], self.fileDict.data[key]['timeStamp']
            except KeyError:
                return config.KEY_ERROR
        else:
            return config.ERR_DEP

if __name__ == "__main__":
    pass