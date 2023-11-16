"""
CSV tracer for the CBD Simulator.
"""

from .baseTracer import BaseTracer

class CSVTracer(BaseTracer):
	"""
	CSV tracer for the CBD Simulator.

	Note:
		During the simulation, all intermediary results will be constantly
		written to the file.
	"""
	def startTracer(self, recover=False):
		super().startTracer(recover)
		self.traceln(",".join(["time"] + self._interpolator.get_header()))

	def traceEndNewIteration(self, _, time):
		if self._interpolator.is_ci_set():
			cnt = self._interpolator.get_deltas_passed(time)
			for i in range(cnt):
				x = self._interpolator.get_next_computation_point()
				if x <= time:
					vals = self._interpolator.compute(x)
					self.traceln(",".join([str(x)] + [str(v) for v in vals]))
				self._interpolator.update_time()
			self._interpolator.post_compute()
		else:
			# NOTE: multi-rate simulation assumes zero-order hold, thus this will be valid
			res = [time]
			for sig in self._interpolator.get_header():
				res.append(self._interpolator.get_curr_signal(sig)[1])
			self.traceln(",".join([str(x) for x in res]))

