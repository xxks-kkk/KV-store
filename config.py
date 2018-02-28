import sys

# WATCHDOG_PORT = 6666
WATCHDOG_PORT = [6666, 6667, 6668, 6669, 6670]
# CLIENT_PORT = 8888
CLIENT_PORT = [9001, 9002, 9003, 9004, 9005]
SERVER_PORT = [8000, 8001, 8002, 8003, 8004]
LOG_FILE = sys.stdout
file_dict_dir = "dict/"
LOG_DIR = "log/"
WRITE_LOG = "W" # Write log
SUCCESS_LOG = "S" # Success log
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

SERVER_COUNT = 5
CLIENT_COUNT = 5
WATCHDOG_IP_LIST = ["localhost"] * SERVER_COUNT
CLIENT_IP_LIST = ["localhost"] * CLIENT_COUNT
GOSSIP_INTERVAL = 0.2
# time period we resend the message to the server that hasn't ACK our message
RESEND_INTERVAL = 1
STABILIZE_INTERVAL = 0.5

# Error message
KEY_ERROR = "ERR_KEY"
ERR_DEP = "ERR_DEP"
debug = False

