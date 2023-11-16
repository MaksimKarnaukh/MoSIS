"""
Matlab file tracer for the CBD Simulator.
"""

from .baseTracer import BaseTracer
import re

try:
	import scipy.io as sio

	class MatTracer(BaseTracer):
		"""
		Matlab tracer for the CBD Simulator.

		Note:
			Because of the Matlab file compression, no intermediary files will
			be opened or written to during the simulation.
		"""
		def __init__(self, uid=-1, filename=None):
			super().__init__(uid, filename)
			self.__data = {"time": []}

		def startTracer(self, recover=False):
			for h in self._interpolator.get_header():
				self.__data[h] = []

		def traceEndNewIteration(self, _, time):
			if self._interpolator.is_ci_set():
				cnt = self._interpolator.get_deltas_passed(time)
				for i in range(cnt):
					x = self._interpolator.get_next_computation_point()
					if x <= time:
						vals = self._interpolator.compute(x)
						self.__data["time"].append(x)
						for hix, h in enumerate(self._interpolator.get_header()):
							self.__data[h].append(vals[hix])
					self._interpolator.update_time()
				self._interpolator.post_compute()
			else:
				# NOTE: multi-rate simulation assumes zero-order hold, thus this will be valid
				self.__data["time"].append(time)
				for sig in self._interpolator.get_header():
					self.__data[sig].append(self._interpolator.get_curr_signal(sig)[1])

		def stopTracer(self):
			data = {}
			for k, v in self.__data.items():
				data[re.sub('[^0-9a-zA-Z]+', "_", k)] = v
			sio.savemat(self.filename, data)

except ImportError:
	raise ImportError("Can not import MatTracer without scipy.")

