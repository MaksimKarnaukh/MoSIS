"""
Custom time module to keep things platform- and Python version-independent.
"""
import time as python_time
from ..util import PYTHON_VERSION
import sys

def time():
	"""
	Gets the correct system time, independent of the Python version or the
	platform.
	"""
	if PYTHON_VERSION == 2:
		if sys.platform == "win32":
			# better precision on windows, but deprecated since 3.3
			return python_time.clock()
		else:
			python_time.time()
	else:
		# return python_time.perf_counter() --> Process specific!
		return python_time.time()

def sleep(t):
	"""
	Sleeps for a while.

	Args:
		t (float):  Amount of seconds to sleep.
	"""
	python_time.sleep(t)
