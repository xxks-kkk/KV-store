# Persistent file dictionary
# Purpose: local KV-store

import config
import json
import os.path

from random import randrange
import datetime
from pprint import pprint

class FileDictionary:
    def __init__(self, id):
        if not os.path.exists(config.file_dict_dir):
            os.makedirs(config.file_dict_dir)
        self.filename = str(id) + '.json'
        self.filepath = os.path.join(config.file_dict_dir, self.filename)
        self.data = self.load() if os.path.isfile(self.filepath) else {}

    def __contains__(self, key):
        return key in self.data

    def put(self, item):
        """
        The structure of item:
            item = {
                'messageId': messageId,
                'key': key,
                'value': value,
                'serverId': serverId,
                'timeStamp': timestamp
            }
        :param item: a dictionary with "key", "val", "serverId", "time"
        :return: None
        """
        self.data[item["key"]] = item

    def get(self, key):
        """
        Get the key-item pair
        :param key: key value
        :return: a dictionary with 'key', 'val', 'time'
        """
        return self.data[key]

    def dump(self):
        with open(self.filepath, 'w') as f:
            json_str = json.dumps(self.data)
            json.dump(json_str, f)

    def load(self):
        with open(self.filepath, 'r') as f:
            json_str = json.load(f)
            data = json.loads(json_str)
        return data

if __name__ == "__main__":
    num_records = 10

    # generate a random list of timestamps
    def random_date(start, l):
        current = start
        while l >= 0:
            curr = current + datetime.timedelta(minutes=randrange(60))
            yield curr
            l -= 1
    startDate = datetime.datetime(2018, 2, 10, 13, 00)
    timestamp_list = random_date(startDate, num_records)

    # Test
    fileDict = FileDictionary(1)
    for key, timestamp in zip(range(num_records), timestamp_list):
        item = {}
        item['key'] = key
        item['value'] = key+1
        item['timeStamp'] = timestamp.strftime("%m/%d/%y %H:%M")
        item['serverId'] = 1
        fileDict.put(item)
    print(fileDict.get(0))
    fileDict.dump()
    data = fileDict.load()
    pprint(data)
