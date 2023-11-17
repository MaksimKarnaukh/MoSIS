"""
This module contains the library building blocks to handle
input/output in the form of file interaction.
"""

from pyCBD.Core import BaseBlock
import csv

class Interpolation:
	"""
	Helper class to handle CSV interpolations.
	"""
	FIRST = 0
	"""Use the first value to interpolate."""

	LAST = 1
	"""Use the last value to interpolate."""

	LINEAR = 2
	"""Do a linear interpolation between the two values."""

	@staticmethod
	def interpolate(a, b, t, method=FIRST):
		"""
		Interpolates between two elements. When :code:`t` corresponds to :code:`a[0]`,
		:code:`a[1]` will always be returned.

		Args:
			a (tuple):      A pair :code:`(time, value)`; representing the first element.
			b (tuple):      A pair :code:`(time, value)`; representing the second element.
			t (float):      The time at which the interpolation happens.
			method (int):   The interpolation method to use.

		Raises:
			AssertionError: When :code:`a[0] <= t < b[0]` is not satisfied.
		"""
		assert a[0] <= t < b[0]
		if t == a[0]:
			return a[1]
		if method == Interpolation.FIRST:
			return a[1]
		if method == Interpolation.LAST:
			return b[1]
		if method == Interpolation.LINEAR:
			return (b[1] - a[1]) / (b[0] - a[0]) * (t - a[0]) + a[1]


class ReadCSV(BaseBlock):
	"""
	Reads data from a CSV file and outputs it on the corresponding timestamps.
	The output ports are defined by the read CSV columns.

	Warning:
		It is required to have a column that represents the time. Furthermore,
		the dataset must be sorted w.r.t. this column.

	Important:
		When repeating, the last value of the CSV is used for time 0.0, hence it
		is prohibited to use time 0 in your CSV.

	Args:
		block_name (str):       The name of the block.
		file_name (str):        The name of the CSV to read.
		hold (Interpolation):   How the data should be interpreted if the time falls
								in-between the records of the (sampled) CSV.
		time_col (str):         The name of the column identifying the time.
								Defaults to :code:`"time"`.
		repeat (bool):          When :code:`True`, the CSV will repeat when at end.
								Additionally, when the time is before the first time
								in the file, an interpolation is done between the last
								read and first read value. When :code:`False`, the
								first and last values will be outputted when lower/higher
								than the predefined range of times.
								Defaults to :code:`False`.

	Keyword Args:
		columns (iter):         A :class:`set`, :class:`list` or a :class:`dict`,
								identifying all columns that need to be read. Must
								correspond to the columns that can be found in the
								file itself. When :code:`None` (default), all
								columns from the first line of the file will be used.
								In the case of a :class:`dict`, it is expected the
								keys are the column names and the values refer to
								the data types of these columns.
								I.e. :code:`{ "time": float }` reads the :code:`time`
								column as floats.
								For :class:`set` and :class:`list`, the data is read
								as strings.
		dtype:                  The default data type of the CSV. This does not override
								optional values set by the :code:`columns` argument when it's
								a :class:`dict`. Defaults to :code:`float`.
		dialect (str):          The dialect for parsing the data. Defaults to :code:`excel`.
		nan (Any):              The value to insert when some fields are missing data.
								Defaults to :code:`None`.
		**:                     For other values, take a look at the
								`CSV Dialect and Formatting Parameters <https://docs.python.org/3/library/csv.html#csv-fmt-params>`_.
	"""
	def __init__(self, block_name, file_name, hold=Interpolation.FIRST, time_col="time", repeat=False, **kwargs):
		self.repeat = repeat
		self.time_col = time_col
		self.__read_file(file_name, **kwargs)
		BaseBlock.__init__(self, block_name, [], [x for x in self.data.keys() if x != time_col])
		self.hold = hold
		self.index = -1

	def __read_file(self, file_name, columns=None, dtype=float, dialect='excel', nan=None, **kwargs):
		"""
		Reads a CSV file into memory.

		Args:
			file_name (str):    The name of the file to read.
			columns (iter):     A collection of column names. When :code:`None`,
								the first row of the file will be used. When a
								dictionary, the keys are the column names and the
								values are the types for the values in the columns.
								Defaults to :code:`None`.
			dtype (type):       The type of all values in the data. When
								:attr:`columns` is a dictionary, this parameter will
								be ignored. Defaults to :code:`float`.
			dialect (str):      The dialect to use in parsing. See also
								`the csv module documentation <https://docs.python.org/3/library/csv.html>`_.
								Defaults to :code:`"excel"`.
			nan:                The value to fill records with if their value is missing.
								Defaults to :code:`None`.
			**kwargs:           See `the csv.reader documentation formatting params
								<https://docs.python.org/3/library/csv.html#csv.reader>`_
		"""
		self.data = {}
		if columns is not None and self.time_col not in columns:
			if isinstance(columns, list):
				columns.append(self.time_col)
			elif isinstance(columns, set):
				columns.add(self.time_col)
			elif not isinstance(columns, dict):
				raise ValueError("Invalid column iterable '{}'".format(type(columns)))
		if columns is not None and isinstance(columns, dict):
			columns[self.time_col] = float
			dtype = str
		with open(file_name) as file:
			reader = csv.DictReader(file, restkey=None, restval=nan, dialect=dialect, **kwargs)
			for row in reader:
				if columns is None:
					columns = row.keys()
				for col in columns:
					if col not in row.keys():
						raise ValueError("Unknown column '{}' in CSV".format(col))
					value = dtype(row[col])
					if isinstance(columns, dict):
						value = columns[col](value)
					self.data.setdefault(col, []).append(value)
		if len(self.data[self.time_col]) == 0:
			raise ValueError("CSV is empty")
		if self.repeat and self.data[self.time_col][0] == 0.0:
			raise ValueError("A repeating CSV series must not start at time 0")

	def compute(self, curIteration):
		time = self.getClock().getTime(curIteration)
		T = self.data[self.time_col][-1]
		L = len(self.data[self.time_col])
		data = {k: self.data[k] for k in self.data if k != self.time_col}
		if L == 1:
			for col in data:
				self.appendToSignal(self.data[col][0], col)
			return
		if not self.repeat:
			first_time = self.data[self.time_col][0]
			if time <= first_time:
				for col in data:
					self.appendToSignal(self.data[col][0], col)
				return
			elif time >= T:
				for col in data:
					self.appendToSignal(self.data[col][-1], col)
				return
			if self.index < 0:
				self.index = 0
		if self.index < 0:
			next_time = last_time = 0.0
		else:
			next_time = last_time = self.data[self.time_col][self.index % L] + (T * (self.index // L))
		while next_time <= time:
			self.index += 1
			last_time = next_time
			next_time = self.data[self.time_col][self.index % L] + (T * (self.index // L))
		self.index -= 1
		# if self.index >= L:
		# 	self.index %= L
		for col in data:
			a = last_time, self.data[col][self.index % L]
			b = next_time, self.data[col][(self.index + 1) % L]
			val = Interpolation.interpolate(a, b, time, self.hold)
			self.appendToSignal(val, col)

	def _rewind(self):
		BaseBlock._rewind(self)
		self.index = -1


class WriteCSV(BaseBlock):
	"""
	Outputs data to a CSV file.
	Every time a message is received, a new record is added to the file. At the
	end of the execution, when this block is destroyed, the file pointer will be
	closed (and removed).

	Args:
		block_name (str):   The name of the block.
		filename (str):     The name of the file to write to. All contents of this
							file will be cleared.
		columns (list):     The (ordered) names of the columns in the file. These
							generally represent the input ports for this block.
		time_col (str):     The name for the column to store the times. If this
							corresponds to a value listed in the :code:`columns`
							argument, that column will be used to keep track of the
							time. There will **never** be an input port called
							:code:`time_col`. If this value is not located in the
							:code:`columns` list, a new column is added to the
							front of the provided columns.
							Defaults to :code:`"time"`.

	:Keyword Arguments:
		Take a look at the `csv.DictWriter <https://docs.python.org/3/library/csv.html#csv.DictWriter>`_
		class for more info.

	Tip:
		When the time-value is not needed in the CSV, just ignore it when reading it out again.
	"""
	def __init__(self, block_name, filename, columns, time_col="time", **kwargs):
		BaseBlock.__init__(self, block_name, [c for c in columns if c != time_col], [])
		self.file = open(filename, 'w', newline='')
		self.columns = columns
		self.time_col = time_col
		if time_col not in columns:
			columns.insert(0, time_col)
		self.writer = csv.DictWriter(self.file, columns, **kwargs)
		self.writer.writeheader()

	def __del__(self):
		self.file.close()

	def compute(self, curIteration):
		inputs = { col: self.getInputSignal(curIteration, col).value for col in self.columns if col != self.time_col }
		inputs[self.time_col] = self.getClock().getTime(curIteration)

		self.writer.writerow(inputs)
