import sys

WATCHDOG_PORT = 6666
CLIENT_PORT = 8888
LOG_FILE = sys.stdout
file_dict_dir = "dict/"

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
