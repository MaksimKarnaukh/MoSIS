from pyCBD.Core import BaseBlock
from threading import Lock


class CollectorBlock(BaseBlock):
	"""
	Abstract class, representing a basic collection unit.
	In the data attribute, a set of values is stored for
	external access (possibly during the simulation).
	This should allow for live plots w.r.t. an independent
	plotting framework.

	Args:
		block_name (str):   The name of the block.
		input_ports (list): The inputs for the collector.
		data (Any):         The data that is being tracked.
	"""
	def __init__(self, block_name, input_ports, data=None):
		BaseBlock.__init__(self, block_name, input_ports, [])
		self._data = data

	def compute(self, curIteration):
		raise NotImplementedError()

	def clear(self):
		"""
		Clears the contents of the block. Must be called in-between
		simulations if the obtainable statistics do not need to
		interfere/retain information about previous simulations.
		"""
		raise NotImplementedError()

	@property
	def data(self):
		"""
		Property to obtain the internal data.
		"""
		return self._data

	def _rewind(self):
		self._data.pop()


class SignalCollectorBlock(CollectorBlock):
	"""
	Collects a single signal to store w.r.t. the arrival time.

	Args:
		block_name (str):   The name of the block.
		buffer_size (int):  The maximal amount of values to keep track of.
							When negative, no buffering will happen.
							Defaults to :code:`-1`.
	"""
	def __init__(self, block_name, buffer_size=-1):
		CollectorBlock.__init__(self, block_name, ["IN1"], [])
		self.buffer_size = buffer_size

	def compute(self, curIteration):
		time = self.getClock().getTime(curIteration)
		value = self.getInputSignal(curIteration, "IN1").value
		self._data.append((time, value))
		if self.buffer_size > 0:
			self._data = self._data[-self.buffer_size:]

	def clear(self):
		self.data.clear()

	@property
	def data_xy(self):
		"""
		The collected data, as a pair of lists; i.e. the unzipped form of
		:code:`xs, ys`.
		"""
		D = self.data[:]
		return [x for x, _ in D], [y for _, y in D]


class PositionCollectorBlock(CollectorBlock):
	"""
	Collects a X/Y position, to be used for a parametric plot.

	Args:
		block_name (str):   The name of the block.
		buffer_size (int):  The maximal amount of values to keep track of.
							When negative, no buffering will happen.
							Defaults to :code:`-1`.
	"""
	def __init__(self, block_name, buffer_size=-1):
		CollectorBlock.__init__(self, block_name, ["X", "Y"], [])
		self.distance_travelled = 0.0
		self.buffer_size = buffer_size

	def compute(self, curIteration):
		x, y = self.getInputSignal(curIteration, "X").value, self.getInputSignal(curIteration, "Y").value
		self.distance_travelled += self.distance_from_last(x, y)
		self._data.append((x, y))
		if self.buffer_size > 0:
			self._data = self._data[-self.buffer_size:]

	def clear(self):
		self.data.clear()

	def distance_from_last(self, x1, y1):
		"""
		Computes the distance between the last point and the given point.

		Args:
			x1 (numeric):   The x position of the given point.
			y1 (numeric):   The y position of the given point.
		"""
		if len(self.data) == 0:
			return 0.0
		x2, y2 = self.data[-1]

		return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

	def distance_from_start(self):
		"""Obtains the distance from the starting position (in the buffer)."""
		if len(self.data) < 2:
			return 0.0
		x1, y1 = self.data[0]
		x2, y2 = self.data[-1]

		return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

	@property
	def data_xy(self):
		"""
		The collected data, as a pair of lists; i.e. the unzipped form of
		:code:`xs, ys`.
		"""
		D = self.data[:]
		return [x for x, _ in D], [y for _, y in D]


class StatisticsCollectorBlock(CollectorBlock):
	"""
	Collects all inputs and allows for statistical data summaries.

	While this can be done on the :class:`SignalCollectorBlock`,
	this class uses a less memory-intensive algorithm to do so.
	When only statistical info is required and a lot of data needs to
	be analyzed, this algorithm should be used!

	Note:
		This block only works for **NUMERICAL** data.
	"""
	def __init__(self, name):
		CollectorBlock.__init__(self, name, ["IN1"], {})
		self.clear()

	def compute(self, curIteration):
		data = self.getInputSignal(curIteration, "IN1").value
		self.data["count"] += 1
		self.data["sum"] += data
		self.data["sumOfSquares"] += data ** 2.0
		self.data["min"] = min(self.data["min"], data)
		self.data["max"] = max(self.data["max"], data)

	def clear(self):
		"""
		Resets the values of the statistics.
		Should be called when the model is used in multiple
		simulations back-to-back to make sure the statistics
		remain valid.
		"""
		self.data["count"] = 0
		self.data["sum"] = 0.0
		self.data["sumOfSquares"] = 0.0
		self.data["min"] = float('inf')
		self.data["max"] = -float('inf')

	def count(self):
		"""
		Returns the amount of items that have been captured.
		"""
		return self.data["count"]

	def min(self):
		"""
		Returns the smallest value that was seen.
		"""
		return float(self.data["min"])

	def max(self):
		"""
		Returns the largest value that was seen.
		"""
		return float(self.data["max"])

	def sum(self):
		"""
		Returns the sum of all items that have been captured.
		"""
		return float(self.data["sum"])

	def sumOfSquares(self):
		"""
		Returns the sum of the squares for all items that have been captured.
		"""
		return float(self.data["sumOfSquares"])

	def mean(self):
		"""
		Returns the average/mean value of the data.
		"""
		if self.count() == 0:
			return 0.0
		return self.sum() / self.count()

	def variance(self):
		"""
		Returns the variance of the data.
		"""
		mu = self.mean()
		n = self.count()
		s = self.sum()
		sq = self.sumOfSquares()
		if n == 0:
			return 0.0
		return sq / n + mu ** 2.0 - (2.0 * mu * s) / n

	def std(self):
		"""
		Returns the standard deviation value of the data.
		"""
		return self.variance() ** 0.5
