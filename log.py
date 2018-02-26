# Implements writeLog structure

import config
import json
import os.path

class Log:
    def __init__(self, id):
        if not os.path.exists(config.LOG_DIR):
            os.makedirs(config.LOG_DIR)
        self.filename = str(id) + config.WRITE_LOG + '.json'
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
    item = {"key": 1, "value": 2, "serverId": 3, "timeStamp": 4, "messageId": 5}
    serverId = 1
    messageId = 10
    messageId2 = 11
    writeLog = Log(serverId)
    writeLog[messageId] = ["put", item, [0]*5]
    print(writeLog[messageId][2][1])
    writeLog[messageId2] = ["put", item, [0]*5]
    print(writeLog)
    del writeLog[messageId2]
    print(writeLog)
    writeLog.dump()
    writeLog2 = Log(serverId)
    print("writeLog2: ", repr(writeLog2))