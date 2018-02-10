# Persistent file dictionary
# Purpose: local KV-store

import config
import json
import os.path

class FileDictionary:
    def __init__(self, id):
        self.filename = str(id) + '.json'
        self.data = self._load() if os.path.isfile(os.path.join(config.file_dict_dir, self.filename)) else {}

    def put(self, key, value, timestamp):
        item = {
            'key': key,
            'val': value,
            'time': timestamp
        }
        self.data[key] = item

    def get(self, key):
        return self.data[key][key]

    def _dump(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f)

    def _load(self):
        with open(self.filename, 'r') as f:
            data = json.load(f)
        return data
