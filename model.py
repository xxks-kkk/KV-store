# Purpose: logic layer on top of server
# (handling put/get requests)

class Model:

    writeLog = None
    """
    [
    "UUID": ["key", "value", "timeStamp", "serverId", "receiptVector"],
    "UUID": ["key", "value", "timeStamp", "serverId", "receiptVector"],
    ]
    """
    def __init__(self, server):
        self.server = server
        pass

    # def onStablize(self):
    #     pass

    def onPrintStore(self):
        # return the dictionary content to a string
        pass

    def put_internal(self, item):
        """
        item as a dictionary:
        "key", "value", "serverId", "timeStamp"
        """
        pass

    def put(self, item):
        """
        item as a dictionary:
        "key", "value", "serverId", "timeStamp"
        """
        pass

    def get(self, key):
        """
        return according to API specification.
        """
        pass
