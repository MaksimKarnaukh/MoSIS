import time as python_time
import sys

def time():
    if sys.version_info[0] == 2 and sys.platform == "win32":
        # better precision on windows, but deprecated since 3.3
        return python_time.clock()
    else:
        return python_time.perf_counter()

def sleep(t):
    python_time.sleep(t)
