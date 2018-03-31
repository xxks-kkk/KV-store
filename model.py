# Purpose: logic layer on top of server
# (handling put/get requests)

from twisted.python import log
import uuid
import file_dict
import config
import clock
from log import Log

from signal import SIGINT, SIGTERM, SIGKILL
from pysigset import suspended_signals

class Model:
    RECEIPT_IDX = 2
    """
    [
    "UUID": ["key", "value", "timeStamp", "serverId", "receiptVector"],
    "UUID": ["key", "value", "timeStamp", "serverId", "receiptVector"],
    ]
    """
    def __init__(self, serverProxy):
        self.serverProxy = serverProxy
        self.writeLog = Log(serverProxy.serverId, "W")
        self.successLog = Log(serverProxy.serverId, "S")
        self.receiptVector = [0] * config.NUM_SERVER
        self.receiptVector[self.serverProxy.serverId] = 1
        self.fileDict = file_dict.FileDictionary(serverProxy.serverId)

    def printStore(self): # return the dictionary content to a string
        # content = ""
        # keys = sorted(list(self.fileDict.data.keys()))
        # for key in keys:
        #     content +=  str(key) + ":" + str(self.fileDict.data[key]['value']) + "\n"
        return {k : v["value"] for k, v in self.fileDict.data.items()}

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
        # log.msg("Key [{}] received[internal]: {}".format(key, item), system=self.serverProxy.tag)
        if key not in self.fileDict or clock.isHappenBefore(self.fileDict[key]['serverId'],
                                                         clock.Clock(self.fileDict[key]['timeStamp']),
                                                         serverId,
                                                         clock.Clock(timeStamp)):
            # Our server doesn't have this KV pair or our KV pair is outdated
            self.fileDict.put(item)
        self.serverProxy.sendMessage({"ReceiverId": serverId,
                                     "MessageId": messageId,
                                     "Method": "Ack",
                                     "Payload": self.serverProxy.serverId})

    def ack(self, message):
        msgId = message.get("MessageId", None)
        if not msgId:
            log.msg("MessageId does not exists: {}".format(message),
                system=self.serverProxy.tag)
            return
        if msgId in self.successLog:
            return
        if msgId not in self.writeLog:
            log.msg("MessageId not in writeLog: {}".format(message),
                system=self.serverProxy.tag)
            return
        item = self.writeLog[msgId]
        senderId = int(message["Payload"])
        item[self.RECEIPT_IDX][senderId] = 1
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
        # log.msg("Key {} received: {}".format(item["key"], item))
        with suspended_signals(SIGKILL, SIGINT, SIGTERM):
            # Signals (SIGKILL, SIGINT, SIGTERM) are blocked here
            self.fileDict.put(item)
            self.writeLog[id] = ["put", item, list(self.receiptVector)]
        # Any pending signal is fired now ...
        for i in range(config.NUM_SERVER):
            if i != self.serverProxy.serverId:
                self.serverProxy.sendMessage({"ReceiverId": i, "MessageId": id, "Method": "Put", "Payload": item})
                # "Payload" means the content send to the network

    def get(self, key, timeStamp):
        """
        return according to API specification.
        """
        if timeStamp is None or clock.isHappenBefore(0, clock.Clock(timeStamp), 0, self.serverProxy.timeStamp):
            try:
                return self.fileDict.data[key]['value']
            except KeyError:
                return config.KEY_ERROR if timeStamp is None else config.ERR_DEP
        else:
            return config.ERR_DEP

    def status(self, on_machines):
        # log.msg("Status called with {}.".format(on_machines), system=self.serverProxy.tag)
        for messageId in self.writeLog:
            receiptVector = self.writeLog[messageId][self.RECEIPT_IDX]
            for i, stat in enumerate(on_machines):
                if stat and receiptVector[i] != 1:
                    return False
        return True

    def dump(self):
        # We save the fildDict and writeLog to the disk
        self.fileDict.dump()
        self.writeLog.dump()

    def resend(self):
        # We want to constant check our writeLog and resend the message
        # to the server that hasn't ack our message
        for messageId in self.writeLog:
            for server_id in range(config.NUM_SERVER):
                if self.writeLog[messageId][self.RECEIPT_IDX][server_id] == 1:
                    pass
                else:
                    self.serverProxy.sendMessage({"ReceiverId": server_id, "MessageId": messageId, "Method": "Put", "Payload": self.writeLog[messageId][1]})

if __name__ == "__main__":
    pass
