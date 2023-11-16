import math


def lerp(x0, y0, x1, y1, x):
	"""
	Linear interpolation method.

	Args:
		x0: first x-coordinate
		y0: first y-coordinate
		x1: second x-coordinate
		y1: second y-coordinate
		x: point to interpolate at

	Returns:
		The interpolated y-value at x for the line segment between (x0, y0) and (x1, y1).

	Raises:
		AssertionError when the value is outside the boundaries, or when the boundaries
		are invalid.
	"""
	if x <= x0:
		return y0
	if x1 <= x:
		return y1
	return (y1 - y0) / (x1 - x0) * (x - x0) + y0


class Interpolator:
	"""
	Interpolation class to be used when a communication interval is set.

	Args:
		ci (numeric):           Communication interval. This is the fixed rate at
								which data is communicated to the end-user.
		method (callable):      Method for the interpolation. Must be a function
								that takes 2 coordinates and another x-value to
								interpolate at in the form of
								:code:`x0, y0, x1, y1, x`. This must return a
								single value. Defaults to :meth:`Interpolator.linear`.
		start_time (numeric):   Starting time for the simulation. Defaults to 0.
	"""
	def __init__(self, ci=0.0, method=lerp, start_time=0.0):
		self.__ci = ci
		self.__header = []
		self.__method = method
		self.__start_time = start_time
		self.__prec = self.get_precision()

		self.__last_time = self.__start_time - self.__ci
		self.__last_signals = {}
		self.__curr_signals = {}

	def __repr__(self):
		return "Interpolator <%.2f> %s" % (self.__ci, str(self.__header))

	def set_header(self, header):
		"""
		Sets the ordering of signals.

		Args:
			header (list):  Ordered list with all the signals to take into account.
		"""
		self.__header = header

	def get_header(self):
		"""
		Gets the current ordering of the signals.
		"""
		return self.__header

	def is_ci_set(self):
		"""
		Checks if the communication interval is set. Otherwise, normal signal outputs will be
		yielded.

		Returns:
			:code:`True` if the communication interval is set.
		"""
		return self.__ci > 0

	def put_signal(self, symbol, signal):
		"""
		Adds a signal to interpolate.

		Args:
			symbol (str):   The symbol to look at.
			signal (tuple): The signal to store.
		"""
		assert symbol in self.__header, "Can only add a signal that is in the header;\n\t%s not found in %s." %(symbol, str(self.__header))
		self.__curr_signals[symbol] = signal
		if symbol not in self.__last_signals:
			self.__last_signals[symbol] = signal

	def get_curr_signal(self, symbol):
		"""
		Gets the current signal for a certain symbol.

		Args:
			symbol (str):   The symbol to look at.
		"""
		return self.__curr_signals[symbol]

	def is_delta_passed(self, current_time):
		"""
		Checks if the delta has passed too much.

		Args:
			current_time (numeric): The current time of the simulation.

		Returns:
			:code:`True` if a new :meth:`compute` must be called.
		"""
		return (current_time - self.__last_time) >= self.__ci

	def get_deltas_passed(self, current_time):
		"""
		Get how many deltas have passed since the last iteration computation.
		This is the amount of values to output.

		Args:
			current_time (numeric): The current time of the simulation.

		Returns:
			How many iterations have passed since the last computation.
		"""
		return math.floor((current_time - self.__last_time) / self.__ci)

	def get_closest_time(self, current_time):
		"""
		Compute the closest time in communication intervals.

		Args:
			current_time (numeric): The current simulation time.

		Returns:
			The closest communication interval value.
		"""
		return current_time - math.fmod(current_time, self.__ci)

	def get_next_computation_point(self):
		"""
		Get the next point at which the compute must be called.
		"""
		return self.__last_time + self.__ci

	def get_precision(self):
		"""
		Obtains the communication interval precision as a multitude of 3.

		Warning:
			The simulator is accurate to the microsecond-level. A value
			higher than 6 might yield undefined behaviour.

		Returns:
			An exponent that indicates the precision of the communication
			interval.

			- 0 means 'seconds'
			- 3 means 'milliseconds'
			- 6 means 'microseconds'
			- 9 means 'nanoseconds'
			- 12 means 'picoseconds'
			- 15 means 'femtoseconds'
		"""
		res = len(str(self.__ci).split(".")[1].rstrip('0'))
		res = math.ceil(res / 3) * 3
		return min(res, 15)

	def compute(self, x):
		"""
		Computes all the values that must be outputted.

		Args:
			x (numeric):    The next simulation time.

		Returns:
			An ordered list with all values that must be outputted in this
			iteration.
		"""
		output = []
		for sym in self.__header:
			t0, v0 = self.__last_signals[sym]
			t1, v1 = self.__curr_signals[sym]
			output.append(self.__method(t0, v0, t1, v1, x))
		return output

	def update_time(self):
		"""
		Updates the time after a computation.
		"""
		self.__last_time = round(self.__last_time + self.__ci, self.__prec)

	def post_compute(self):
		"""
		Function to execute at each iteration, but after the compute.
		"""
		self.__last_signals = self.__curr_signals.copy()
		# Do not clear the current signals to allow for multi-rate simulations