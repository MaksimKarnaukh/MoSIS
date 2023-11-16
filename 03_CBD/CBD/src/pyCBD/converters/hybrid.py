"""
This module allows CBD models to be executed inside of a DEVS simulation.

See Also:
	`PythonPDEVS <http://msdl.cs.mcgill.ca/projects/DEVS/PythonPDEVS>`_
"""
from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY
from pyCBD.Core import CBD
from pyCBD.lib.std import *
from pyCBD.lib.endpoints import SignalCollectorBlock
from pyCBD.simulator import Simulator
from pyCBD.realtime.threadingBackend import Platform
from copy import deepcopy

__all__ = ['CBDRunner', 'prepare_cbd', 'CrossingDetection']

import math
class CrossingDetection:
	"""
	Helper class that implements the crossing detection algorithms.

	The following description concerns the default arguments for all functions.
	On top of that, there may be some additional arguments defined, as listed in
	the specific documentations below.

	Args:
		t1 (float):     The x-value of the lower bound of the interval.
		t2 (float):     The x-value of the higher bound of the interval.
		y (float):      The value for which a crossing must be checked.
		f:              A function that should return the y-value for a given x (or t).
	"""
	@staticmethod
	def linear(t1, t2, y, f, **kwargs):
		"""
		Finds the root of the crossing using linear interpolation.
		No additional function calls or arguments are used.
		"""
		y1 = f(t1)
		y2 = f(t2)
		if y1 == y2:
			return y1
		return (t2 - t1) / (y2 - y1) * (y - y1) + t1

	@staticmethod
	def regula_falsi(t1, t2, y, f, **kwargs):
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
		eps = kwargs.get("eps", 1e-5)
		n = kwargs.get("n", 5 * 1000 * 1000)
		y1 = f(t1) - y
		y2 = f(t2) - y
		assert y1 * y2 < 0, "No crossing possible in given range"
		tn, yn = t1, y1
		side = 0
		for i in range(n):
			if abs(t1 - t2) < eps * abs(t1 + t2): break
			tn = (y1 * t2 - y2 * t1) / (y1 - y2)
			yn = f(tn) - y
			if yn * y2 > 0:
				t2, y2 = tn, yn
				if side == -1:
					y1 /= 2
				side = -1
			elif yn * y1 > 0:
				t1, y1 = tn, yn
				if side == 1:
					y2 /= 2
				side = 1
			else:
				break
		return tn

	@staticmethod
	def ITP(t1, t2, y, f, **kwargs):
		r"""Implements the Interpolation-Truncation-Projection algorithm for finding
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
		k1 = kwargs.get("k1", 0.1)
		k2 = kwargs.get("k2", 1.5)
		eps = kwargs.get("eps", 1e-5)
		n0 = kwargs.get("n0", 0)

		assert 0 < k1, "For ITP, k1 must be strictly positive."
		assert 1 <= k2 <= (1 + (1. + 5 ** 0.5) / 2.), "For ITP, k2 must be in [1, 1 + phi]."
		assert 0 <= n0, "For ITP, n0 must be positive or zero."

		sign = lambda x: 1 if x > 0 else (-1 if x < 0 else 0)

		a = t1
		b = t2
		ya = f(a) - y
		yb = f(b) - y

		if ya == 0:
			return a
		if yb == 0:
			return b
		assert ya * yb < 0, "No crossing possible in given range"

		# Preprocessing
		nh = math.ceil(math.log((b - a) / (2 * eps), 2))
		nm = nh + n0
		j = 0

		while (b - a) > (2 * eps):
			xh = (a + b) / 2
			r = eps * 2 ** (nm - j) - (b - a) / 2
			d = k1 * (b - a) ** k2

			# Interpolation
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
			yI = f(xI) - y
			if (ya - yb) * yI < 0:
				b = xI
				yb = yI
			elif (ya - yb) * yI > 0:
				a = xI
				ya = yI
			else:
				a = xI
				b = xI
			j += 1

		return (a + b) / 2


from pyCBD.converters.CBDDraw import gvDraw
class CBDRunner(AtomicDEVS):
	"""
	Atomic DEVS model that can be used to execute a CBD model.

	Args:
		name (str):         The name of the CBD model.
		cbd (pyCBD.Core.CBD): The CBD model to run.
		initials (dict):    The initial conditions for all the inputs.
		stopped (bool):     Whether to start from paused mode or not. In this paused mode, the
							model will not progress. Useful when in combination with multiple
							ODEs. Defaults to :code:`False`.
		crossings (dict):   Dictionary of :code:`{ name -> value }` that defines which
							variable needs to be detected for a crossing through a certain value.
							The value can be a string, starting with either :code:`<`, :code:`>`
							or :code:`=`, which respectively means a crossing from low to high,
							high to low or either side. Notice that :code:`=` is the default
							starting character assumed when the value is a float. When
							:code:`None`, no detection will happen. Defaults to :code:`None`.
		algo:               The root finding algorithm function. See :class:`CrossingDetection`
							for more info.
		**kwargs:           Optional parameters for the zero-crossing detection algorithm.
	"""
	def __init__(self, name, cbd, initials=None, stopped=False, crossings=None, algo=CrossingDetection.ITP, **kwargs):
		AtomicDEVS.__init__(self, name)
		self.initials = {} if initials is None else initials
		self.original_model, self.Hname = prepare_cbd(cbd.clone(), initials)
		self.crossings = {} if crossings is None else crossings
		self.algo = algo
		self.kwargs = kwargs

		self.state = {
			"CBD": None,
			"curIt": 0,
			"delta_t": 0.0,
			"initials": self.initials,
			"request_output": False,
			"request_compute": True,
			"zero_crossing": None,
			"time": 0.0,
			"stopped": stopped
		}

		self.simulator = None
		self.reinit()
		# gvDraw(self.state["CBD"], name + ".dot")

		self.inputs = {}
		for inp in cbd.getInputPortNames():
			self.inputs[inp] = self.addInPort(inp)
		self.stop = self.addInPort("stop")

		self.outputs = {}
		for out in cbd.getOutputPortNames():
			self.outputs[out] = self.addOutPort(out)
		for out in self.crossings:
			self.outputs["crossing-" + out] = self.addOutPort("crossing-" + out)

	def reinit(self):
		"""
		Re-initializes the CBD model.

		Warning:
			Use this function with care. It is expected a simulation will commence
			after this function was called.
		"""
		self.state["CBD"] = self.original_model.clone()
		self.apply_initials()
		self.simulator = Simulator(self.state["CBD"])
		self.simulator.getClock().setStartTime(self.state["time"])
		# self.state["delta_t"] = self.simulator.getDeltaT()
		# self.set_delta(float('inf'))

	def apply_initials(self):
		"""
		Applies the initial values.
		"""
		for k, v in self.state["initials"].items():
			self.state["CBD"].getBlockByName(k).setValue(v)

	def get_signal(self, pname):
		"""
		Gets the output for a given name.

		Args:
			pname (str):    The name of the port.
		"""
		return self.state["CBD"].getSignalHistory(pname)[-1].value

	def crossing_detection(self, signal, y, y0):
		"""
		Crossing root finder for a signal.

		Args:
			signal (str):   The port to detect.
			y (float):      The value to cross.
			y0 (float):     Y-value of the lower end of the interval.
		"""
		def F(t):
			h = t - self.state["time"]
			if h == 0:
				return y0
			return self.crossing_function(h, signal)
		t1 = self.state["time"]
		t2 = t1 + self.state["delta_t"]
		return self.algo(t1, t2, y, F, **self.kwargs)

	def crossing_function(self, h, signal, restore=True):
		"""
		Computes the function value of the simulation after a specified delay.
		This will be used in combination with :class:`CrossingDetection` to
		find the roots of a function.

		This function will first rewind the simulator such that :code:`h` can be
		applied, before stepping until :code:`h` was found. Afterwards, the
		simulation is possibly restored to the original state.

		Args:
			h (float):      The delay.
			signal (str):   The signal that must be read. When :code:`None`,
							no signal will be read.
			restore (bool): When :code:`True`, the simulation will be restored after
							the value was found. Defaults to :code:`True`.
		"""
		oh = self.get_delta()
		self.simulator._rewind()
		# self.simulator._rewind()
		self.set_delta(h)
		# clock.setStartTime(clock.getStartTime() - oh)
		self.simulator._do_single_step()
		# clock.setStartTime(clock.getStartTime() - oh)
		# self.simulator._do_single_step()

		result = None
		if signal is not None:
			result = self.state["CBD"].getSignalHistory(signal)[-1].value

		if restore:
			self.simulator._rewind()
			# self.simulator._rewind()
			self.set_delta(oh)
			# clock.setStartTime(clock.getStartTime() - oh)
			self.simulator._do_single_step()
			# clock.setStartTime(clock.getStartTime() - oh)
			# self.simulator._do_single_step()

		return result

	def set_delta(self, val):
		"""
		Sets the maximal allowed delta of the clock.

		Args:
			val (float):    The maximal allowed delta.
		"""
		clock = self.simulator.getClock()
		clock.setDeltaT(val)
		# self.state["CBD"].getBlockByName(self.Hname).setValue(val)

	def get_delta(self):
		"""
		Obtains the last used delta.
		"""
		return self.simulator.getClock().getInputSignal(-1, 'h').value

	def timeAdvance(self):
		"""
		See Also:
			`PythonPDEVS documentation <https://msdl.uantwerpen.be/documentation/PythonPDEVS/ADEVS_int.html>`_
		"""
		if self.state["stopped"]:
			return INFINITY
		if self.state["request_compute"]:
			return 0.0
		return max(0.0, self.state["delta_t"])

	def outputFnc(self):
		"""
		See Also:
			`PythonPDEVS documentation <https://msdl.uantwerpen.be/documentation/PythonPDEVS/ADEVS_int.html>`_
		"""
		res = {}
		cross = []
		if self.state["zero_crossing"] is not None:
			for c in self.state["zero_crossing"]:
				cross.append("crossing-" + c)
		if self.state["request_output"]:
			for out, port in self.outputs.items():
				if out in cross:
					res[port] = True
				elif not out.startswith("crossing-"):
					res[port] = self.get_signal(out)
		return res

	def intTransition(self):
		"""
		See Also:
			`PythonPDEVS documentation <https://msdl.uantwerpen.be/documentation/PythonPDEVS/ADEVS_int.html>`_
		"""
		ta = self.timeAdvance()
		self.state["time"] += ta
		# TODO: debug === State event location in pypdevs does not work somehow
		# self.set_delta(self.state["delta_t"])
		if self.state["request_output"]:
			self.state["request_output"] = False
			self.state["request_compute"] = True
			return self.state

		self.state["request_output"] = True
		self.state["request_compute"] = False
		self.state["zero_crossing"] = None

		self.state["curIt"] += 1
		if self.state["curIt"] == 1:
			self.simulator._do_single_step()
			self.state["request_output"] = True
			return self.state

		old = {}
		for c in self.crossings:
			# print("PRE", c, self.state["CBD"].getBlockByName(c).getSignalHistory("OUT1")[-1])
			old[c] = self.get_signal(c)

		self.state["delta_t"] = self.get_delta()
		self.simulator._do_single_step()

		cds = {}
		# TODO: can this be computed for all signals at once, instead of signal per signal?
		for z, yq in self.crossings.items():
			value = self.get_signal(z)
			y = yq
			q = '='
			if isinstance(yq, str):
				y = float(yq[1:])
				q = yq[0]
			# print("POST", z, self.state["CBD"].getBlockByName(z).getSignalHistory("OUT1")[-1])
			if (old[z] - y) * (value - y) < 0:
				# A crossing will happen!
				if q == '=' or (q == '<' and old[z] < value) or (q == '>' and old[z] > value):
					cds.setdefault(self.crossing_detection(z, y, old[z]), []).append(z)
		if len(cds) > 0:
			fzc = min(cds)
			self.state["zero_crossing"] = cds[fzc]
			h = fzc - self.state["time"]
			self.state["delta_t"] = h

			# print("CROSSING HAPPENED")

			self.crossing_function(h, None, False)
		else:
			self.set_delta(self.state["delta_t"])
		return self.state

	def extTransition(self, inputs):
		"""
		See Also:
			`PythonPDEVS documentation <https://msdl.uantwerpen.be/documentation/PythonPDEVS/ADEVS_int.html>`_
		"""
		self.state["time"] += self.elapsed

		if not self.state["stopped"]:
			self.state["delta_t"] -= self.elapsed
		else:
			self.state["delta_t"] = 0.0

		if self.stop in inputs and inputs[self.stop]:
			self.simulator.stop()
			self.state["request_output"] = True
			self.state["stopped"] = True
			return self.state

		for inport, value in inputs.items():
			if inport.name in self.initials:
				self.state["initials"][inport.name] = value

		self.reinit()

		self.state["request_compute"] = True
		self.state["request_output"] = False
		self.state["stopped"] = False
		self.state["curIt"] = 0
		self.state["delta_t"] = 0.0
		return self.state

	def __del__(self):
		self.simulator.stop()


from pyCBD.Core import Port

def prepare_cbd(model, initials):
	"""
	Obtains a CBD model that can be executed with the :class:`CBDRunner`.
	The model will be cloned and all input ports will be altered to become constant
	blocks. Additionally, a :class:`pyCBD.lib.std.ConstantBlock` and a
	:class:`pyCBD.lib.std.MinBlock` will be added in-between the Clock and the block
	that connects to the Clock over the :code:`h` input.

	Args:
		model (pyCBD.Core.CBD): The CBD model to prepare.
		initials (dict):        A dictionary in the form of
								:code:`input port name -> initial value`.

	Returns:
		A tuple of :code:`(prepared CBD, name)` where :code:`name` identifies the
		name for the

	Note:
		Usually, this function shouldn't be called by a user.
	"""
	cbd = model.clone()
	for inp in cbd.getInputPorts():
		block = ConstantBlock(inp.name, initials.get(inp.name, 0))
		outs = inp.getOutgoing()[:]
		cbd.removeInputPort(inp.name)
		cbd.addBlock(block)
		for conn in outs:
			Port.disconnect(inp, conn.target)
			Port.connect(block.getOutputPortByName("OUT1"), conn.target)

	# for inp in (b for b in model.getBlocks() if b.getBlockType() == "InputPortBlock"):
	# 	name = inp.getBlockName()
	# 	cbd.removeBlock(inp)
	# 	cbd.addBlock(ConstantBlock(name, initials.get(name, 0)))
	# 	for block in model.getBlocks():
	# 		if block.getBlockType() == "InputPortBlock": continue
	# 		for P in block.getInputPorts():
	# 			if P.block.getBlockName() == name:
	# 				cbd.addConnection(name, block.getBlockName(), input_port_name=k)

	# Set clock minimal H
	Hname = cbd.getUniqueBlockName("H")
	cbd.addBlock(ConstantBlock(Hname, float('inf')))
	Mname = cbd.getUniqueBlockName("Min")
	cbd.addBlock(MinBlock(Mname))
	clock = cbd.getClock()
	cbd.addConnection(Hname, Mname)
	cbd.addConnection(clock.getPortConnectedToInput('h').block, Mname)
	cbd.removeConnection(clock, 'h')
	cbd.addConnection(Mname, clock, input_port_name='h')
	return cbd, Hname

if __name__ == '__main__':
	import numpy as np
	def f(x):
		return np.cos(x) - x ** 3
	print(CrossingDetection.regula_falsi(0, 1.5, 0, f))
	# def f(x):
	# 	return x ** 3 - 2*x
	print(CrossingDetection.ITP(0, 1.5, 0, f, k1=0.1, k2=1.5))
