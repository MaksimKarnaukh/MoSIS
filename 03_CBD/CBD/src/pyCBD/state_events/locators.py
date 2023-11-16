"""
This module contains the standard State Event locators.
"""

import math
from pyCBD.state_events import Direction

__all__ = ['PreCrossingStateEventLocator', 'PostCrossingStateEventLocator', 'LinearStateEventLocator',
           'BisectionStateEventLocator', 'RegulaFalsiStateEventLocator', 'ITPStateEventLocator']

class StateEventLocator:
	"""
	Computes the exact level crossing time and locates when a state event must be scheduled.

	Attributes:
		sim (CBD.simulator.Simulator):  The simulator to which the locator belongs.
		t_lower (float):                The lower range of the level crossing. It is certain
										that the crossing happens at a time later than (or
										equal to) this time.
	"""
	def __init__(self):
		self.sim = None
		self.t_lower = 0.0

	def setSimulator(self, sim):
		"""
		Sets the simulator to the event locator.

		Args:
			sim (CBD.simulator.Simulator):  The current simulator.
		"""
		self.sim = sim

	def detect(self, prev, curr, direction=Direction.ANY):
		"""
		Detects that a crossing through zero happened between prev and curr.

		Args:
			prev (numeric):         The previous value.
			curr (numeric):         The current value.
			direction (Direction):  The direction of the crossing to detect.
									Defaults to :attr:`Direction.ANY`.

		Returns:
			:code:`True` when the crossing happened, otherwise :code:`False`.
		"""
		if direction == Direction.FROM_BELOW:
			return prev <= 0 <= curr
		if direction == Direction.FROM_ABOVE:
			return prev >= 0 >= curr
		if direction == Direction.ANY:
			return (prev <= 0 <= curr) or (prev >= 0 >= curr)

		return False

	def detect_signal(self, output_name, level=0.0, direction=Direction.ANY):
		"""
		Detects that an output port has a crossing through a specific level.

		Args:
			output_name (str):      The name of the output port.
			level (numeric):        The level through which the value must go.
									Defaults to 0.
			direction (Direction):  The direction of the crossing to detect.
									Defaults to :attr:`Direction.ANY`.

		Returns:
			:code:`True` when the crossing happened, otherwise :code:`False`.
		"""
		sig = self.sim.model.getSignalHistory(output_name)
		if len(sig) < 2:
			# No crossing possible (yet)
			return False
		prev = sig[-2].value - level
		curr = sig[-1].value - level

		return self.detect(prev, curr, direction)

	def _function(self, output_name, time, level=0.0, noop=True):
		"""
		The internal function. Whenever an algorithm requires the computation of the
		CBD model at another time, this function can be executed.

		Args:
			output_name (str):  The output port name for which the crossing point must
								be computed.
			time (float):       The time at which the CBD must be computed. Must be
								larger than the lower bound time.
			level (float):      The level through which the crossing must be identified.
								This mainly shifts the signal towards 0, as most algorithms
								are basically root finders. If the algorithm incorporates
								the level itself, keep this value at 0 for correct behaviour.
								Defaults to 0.
			noop (bool):        When :code:`True`, this function will be a no-op. Otherwise,
								the model will remain at the given time.

		Returns:
			The signal value of the output at the given time, shifted towards 0.
		"""
		if callable(output_name):
			return output_name(time) - level
		assert time >= self.t_lower

		h = self.sim.getDeltaT()
		# self.sim._rewind()
		self.setDeltaT(time - self.t_lower)
		self.sim._lcc_compute()
		s = self.sim.model.getSignalHistory(output_name)[-1].value - level

		if noop:
			self.sim._rewind()
		self.setDeltaT(h)
		# if noop:
		# 	self.sim._lcc_compute()
		return s

	def setDeltaT(self, dt):
		"""
		'Forces' the time-delta to be this value for the next computation.
		Args:
			dt (float): New time-delta.
		"""
		# TODO: make this work for non-fixed rate clocks?
		clock = self.sim.getClock()
		clock.setDeltaT(dt)
		# clock.getPortConnectedToInput("h").block.setValue(dt)

	def run(self, output_name, level=0.0, direction=Direction.ANY):
		"""
		Executes the locator for an output.

		Args:
			output_name (str):      The output port name for which the crossing
									point must be computed.
			level (float):          The level through which the crossing must be
									identified. Defaults to 0.
			direction (Direction):  The direction of the crossing to detect.
									Defaults to :attr:`Direction.ANY`.

		Returns:
			The detected time at which the crossing is suspected to occur.
		"""

		sig = self.sim.model.getSignalHistory(output_name)
		p1 = sig[-2].time, sig[-2].value - level
		p2 = sig[-1].time, sig[-1].value - level
		self.t_lower = p1[0]

		# begin the algorithm on the left
		self.sim._rewind()
		t_crossing = self.algorithm(p1, p2, output_name, level, direction)

		return t_crossing

	def algorithm(self, p1, p2, output_name, level=0.0, direction=Direction.ANY):
		"""
		The algorithm that identifies the locator functionality. Must be implemented
		in sub-classes. Should only ever be called if a crossing exists.

		Args:
			p1 (tuple):         The (time, value) coordinate before the crossing,
								shifted towards zero.
			p2 (tuple):         The (time, value) coordinate after the crossing,
								shifted towards zero.
			output_name:        The output port name for which the crossing point
								must be computed, if a CBD is given. Otherwise, a
								single-argument callable :math`f(t)` is accepted
								as well.
			level (float):      The level through which the crossing must be
								identified. Defaults to 0.
			direction (Direction):  The direction of the crossing to detect. This
								value ensures a valid crossing is identified if there
								are multiple between :attr:`p1` and :attr:`p2`. Will
								only provide an acceptable result if the direction of
								the crossing can be identified. For instance, if
								there is a crossing from below, according to the
								:meth:`detect` function, the algorithm will usually
								not accurately identify any crossings from above.
								Defaults to :attr:`Direction.ANY`.

		Returns:
			A suspected time of the crossing.
		"""
		raise NotImplementedError()


class PreCrossingStateEventLocator(StateEventLocator):
	"""
	Assumes that the crossing happens at the start of the interval.
	Can be used if a precise detection is not a requirement.

	This implementation computes a rough under-estimate.
	"""
	def algorithm(self, p1, p2, output_name, level=0.0, direction=Direction.ANY):
		return p1[0]


class PostCrossingStateEventLocator(StateEventLocator):
	"""
	Assumes that the crossing happens at the end of the interval.
	Can be used if a precise detection is not a requirement.

	This implementation computes a rough over-estimate.

	Corresponds to the :code:`if` statement in `Modelica <https://modelica.org/>`_,
	whereas the other locators can be seen as the :code:`when` statement.
	"""
	def algorithm(self, p1, p2, output_name, level=0.0, direction=Direction.ANY):
		return p2[0]


class LinearStateEventLocator(StateEventLocator):
	"""
	Uses simple linear interpolation to compute the time of the crossing.
	This is usually a rough, yet centered estimate.

	This locator should only be used if it is known that the signal is
	(mostly) linear between the lower and upper bounds.
	"""
	def algorithm(self, p1, p2, output_name, level=0.0, direction=Direction.ANY):
		t1, y1 = p1
		t2, y2 = p2
		if y1 == y2:
			return t1
		# Use the equation of a line between two points
		# Formula is easier if x and y axes are swapped.
		return (t2 - t1) / (y2 - y1) * (level - y1) + t1


class BisectionStateEventLocator(StateEventLocator):
	"""
	Uses the bisection method to compute the crossing. This method is more accurate
	than a linear algorithm :class:`LinearStateEventLocator`, but less accurate than
	regula falsi (:class:`RegulaFalsiStateEventLocator`).

	Args:
		n (int):    The maximal amount of iterations to compute. Roughly very 3 iterations,
					a decimal place of accuracy is gained. Defaults to 10.
	"""
	def __init__(self, n=10):
		assert n > 0, "There must be at least 1 iteration for this method."
		super(BisectionStateEventLocator, self).__init__()
		self.n = n

	def algorithm(self, p1, p2, output_name, level=0.0, direction=Direction.ANY):
		tc = p1[0]
		for i in range(self.n):
			tc = ((p2[0] - p1[0]) / 2) + p1[0]
			yc = self._function(output_name, tc, level)

			if self.detect(p1[1], yc, direction):
				p2 = tc, yc
			elif self.detect(yc, p2[1], direction):
				p1 = tc, yc
			else:
				break
				# raise ValueError("Cannot find a viable crossing.")
		return tc


class RegulaFalsiStateEventLocator(StateEventLocator):
	"""
	Implements the Illinois algorithm for finding the root for a crossing problem.

	Args:
		eps (float):    Half of the upper bound for the relative error.
						Defaults to 1e-5.
		n (int):        The maximal amount of iterations to compute. Defaults to
						5 million iterations.

	See Also:
		https://en.wikipedia.org/wiki/Regula_falsi
	"""
	def __init__(self, eps=1e-5, n=5_000_000):
		super(RegulaFalsiStateEventLocator, self).__init__()

		self.eps = eps
		self.n = n

	def algorithm(self, p1, p2, output_name, level=0.0, direction=Direction.ANY):
		# direction unused, because the algorithm will automatically maintain
		#   the crossing direction
		t1, y1 = p1
		t2, y2 = p2
		tn, yn = t1, y1

		y1 -= level
		y2 -= level

		side = 0
		for i in range(self.n):
			if abs(t1 - t2) < self.eps * abs(t1 + t2): break
			if abs(y1 - y2) < self.eps:
				tn = (t2 - t1) / 2 + t1
			else:
				tn = (y1 * t2 - y2 * t1) / (y1 - y2)
			yn = self._function(output_name, tn, level)

			if self.detect(y1, yn, direction):
				t2, y2 = tn, yn
				if side == -1:
					y1 /= 2
				side = -1
			elif self.detect(yn, y2, direction):
				t1, y1 = tn, yn
				if side == 1:
					y2 /= 2
				side = 1
			else:
				break
		return tn


class ITPStateEventLocator(StateEventLocator):
	r"""
	Implements the Interpolation-Truncation-Projection algorithm for finding
	the root of a function.

	Args:
		eps (float):    Minimal interval size. Defaults to 1e-5.
		k1 (float):     First truncation size hyperparameter. Must be in the
						range of :math:`(0, \infty)`. Defaults to 0.1.
		k2 (float):     Second truncation size hyperparameter. Must be in the
						range of :math:`[1, 1 + \frac{1}{2}(1 + \sqrt{5})]`.
						Defaults to 1.5.
		n0 (float):     Slack variable to control the size of the interval for
						the projection step. Must be in :math:`[0, \infty)`.
						When 0, the average number of iterations will be less
						than that of the bisection method. Defaults to 0.

	See Also:
		https://en.wikipedia.org/wiki/ITP_method
	"""
	def __init__(self, eps=1e-5, k1=0.1, k2=1.5, n0=0):
		assert 0 < k1, "For ITP, k1 must be strictly positive."
		assert 1 <= k2 <= (1 + (1. + 5 ** 0.5) / 2.), "For ITP, k2 must be in [1, 1 + phi]."
		assert 0 <= n0, "For ITP, n0 must be positive or zero."

		super(ITPStateEventLocator, self).__init__()

		self.eps = eps
		self.k1 = k1
		self.k2 = k2
		self.n0 = n0

	def algorithm(self, p1, p2, output_name, level=0.0, direction=Direction.ANY):
		sign = lambda x: 1 if x > 0 else (-1 if x < 0 else 0)

		a, ya = p1
		b, yb = p2

		ya -= level
		yb -= level

		if ya == 0:
			return a
		if yb == 0:
			return b

		# Preprocessing
		nh = math.ceil(math.log((b - a) / (2 * self.eps), 2))
		nm = nh + self.n0
		j = 0

		while (b - a) > (2 * self.eps):
			xh = (b - a) / 2 + a
			r = self.eps * 2 ** (nm - j) - (b - a) / 2
			d = self.k1 * (b - a) ** self.k2

			# Interpolation
			if abs(yb - ya) < self.eps:
				xf = xh
			else:
				xf = (yb * a - ya * b) / (yb - ya)

			# Truncation
			s = sign(xh - xf)
			if d <= abs(xh - xf):
				xt = xf + s * d
			else:
				xt = xh

			# Projection
			if abs(xt - xh) <= r:
				xI = xt
			else:
				xI = xh - s * r

			# Update Interval
			yI = self._function(output_name, xI, level)
			if (ya - yb) * yI < 0 and self.detect(ya, yI, direction):
				b = xI
				yb = yI
			elif (ya - yb) * yI > 0 and self.detect(yI, yb, direction):
				a = xI
				ya = yI
			else:
				a = xI
				b = xI
			j += 1

		return (a + b) / 2
