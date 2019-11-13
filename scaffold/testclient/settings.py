REDIS_CONNECT_KWARGS = {"db": 0}
NUM_DEVICES = 2
NUM_DEVICE_TYPES = 2
DEVICE_TYPE_EQUALITY = True
FLUSH_ON_START = True
SERVER_ENTRY_POINT_URL = "localhost"
SERVER_ENTRY_POINT_HEADERS = None
try:
    from settings_local import *
except ImportError:
    print("not found")
