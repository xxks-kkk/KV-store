# Implements writeLog structure

import config
import json
import os.path

class Log:
    def __init__(self, id, mode):
        """
        Initialization
        :param id: serverId; used to naming the log file on disk
        :param mode: whether it is a writeLog or a successLog
        """
        if not os.path.exists(config.LOG_DIR):
            os.makedirs(config.LOG_DIR)
        if mode == "W":
            self.filename = str(id) + config.WRITE_LOG + '.json'
        elif mode == "S":
            self.filename = str(id) + config.SUCCESS_LOG + '.json'
        self.filepath = os.path.join(config.LOG_DIR, self.filename)
        self.data = self.load() if os.path.isfile(self.filepath) else {}

    def load(self):
        with open(self.filepath, 'r') as f:
            json_str = json.load(f)
            data = json.loads(json_str)
        return data

    def dump(self):
        with open(self.filepath, 'w') as f:
            json_str = json.dumps(self.data)
            json.dump(json_str, f)

    def __contains__(self, item):
        """
        Support "in" operator
        :param item:
        :return:
        """
        return item in self.data

    def __getitem__(self, item):
        """
        Support get element using []
        :param item:
        :return:
        """
        return self.data[item]

    def __iter__(self):
        return self.data.__iter__()

    def __next__(self):
        return self.data.__next__()

    def __setitem__(self, key, value):
        """
        Support set element using []
        :param key:
        :param value:
        :return:
        """
        self.data[key] = value

    def __delitem__(self, key):
        """
        Support del
        :param key:
        :return:
        """
        del self.data[key]

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return str(self.data)


if __name__ == "__main__":

    def unit_test_writeLog():
        """
        Unit test for writeLog
        :return:
        """
        print("Unit test for writeLog")
        item = {"key": 1, "value": 2, "serverId": 3, "timeStamp": 4, "messageId": 5}
        serverId = 1
        messageId = 10
        messageId2 = 11
        writeLog = Log(serverId, "W")
        writeLog[messageId] = ["put", item, [0]*5]
        print(writeLog[messageId][2][1])
        writeLog[messageId2] = ["put", item, [0]*5]
        print(writeLog)
        del writeLog[messageId2]
        print(writeLog)
        writeLog.dump()
        writeLog2 = Log(serverId, "W")
        print("writeLog2: ", repr(writeLog2))

    def unit_test_successLog():
        """
        Unit test for successLog
        :return:
        """
        print("Unit test for successLog")
        item = {"key": 1, "value": 2, "serverId": 3, "timeStamp": 4, "messageId": 5}
        serverId = 1
        messageId = 10
        messageId2 = 11
        successLog = Log(serverId, "S")
        successLog[messageId] = item
        print(successLog[messageId])
        successLog[messageId2] = item
        print(successLog)
        del successLog[messageId2]
        print(successLog)
        successLog.dump()
        successLog2 = Log(serverId, "S")
        print("writeLog2: ", repr(successLog2))

    unit_test_successLog()
    unit_test_writeLog()
