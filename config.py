import sys

WATCHDOG_PORT = 6666
# WATCHDOG_PORT = [6666, 6667, 6668, 6669, 6670]
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
    "0": ('128.83.139.248', 8000, "server"),
    "1": ('128.83.130.139', 8001, "server"),
    "2": ('128.83.120.63', 8002, "server"),
    "3": ('128.83.139.77', 8003, "server"),
    "4": ('128.83.139.114', 8004, "server"),
    "5": ('128.83.139.250', 9001, "client"),
    "6": ('128.83.139.78', 9002, "client"),
    "7": ('128.83.130.140', 9003, "client"),
    "8": ('128.83.130.142', 9004, "client"),
    "9": ("128.83.144.59", 9005, "client"),
}

SERVER_COUNT = 5
CLIENT_COUNT = 5
# WATCHDOG_IP_LIST = ["localhost"] * SERVER_COUNT
# CLIENT_IP_LIST = ["localhost"] * CLIENT_COUNT
WATCHDOG_IP_LIST = ['128.83.139.248','128.83.130.139','128.83.120.63', '128.83.139.77','128.83.139.114']
CLIENT_IP_LIST = ['128.83.139.250','128.83.139.78','128.83.130.140','128.83.130.142','128.83.144.59']

GOSSIP_INTERVAL = 0.2
# time period we resend the message to the server that hasn't ACK our message
RESEND_INTERVAL = 1
STABILIZE_INTERVAL = 0.1
CHECK_INTERVAL = 0.1
DISPLAY_COMMAND = True
# Error message
KEY_ERROR = "ERR_KEY"
ERR_DEP = "ERR_DEP"
DEBUG = True

