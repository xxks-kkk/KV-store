import sys

WATCHDOG_PORT = 6666
CLIENT_PORT = 8888
LOG_FILE = sys.stdout
file_dict_dir = "dict/"
NUM_SERVER = 5

ADDR_PORT = {
    "0": ("localhost", 8000, "server"),
    "1": ("localhost", 8001, "server"),
    "2": ("localhost", 8002, "server"),
    "3": ("localhost", 8003, "server"),
    "4": ("localhost", 8004, "server"),
    "5": ("localhost", 9001, "client"),
    "6": ("localhost", 9002, "client"),
    "7": ("localhost", 9003, "client"),
    "8": ("localhost", 9004, "client"),
    "9": ("localhost", 9005, "client"),
}

localhost =  "127.0.0.1"
SERVER_COUNT = 5
CLIENT_COUNT = 5
WATCHDOG_IP_LIST = [localhost] * SERVER_COUNT
CLIENR_IP_LIST = [localhost] * CLIENT_COUNT