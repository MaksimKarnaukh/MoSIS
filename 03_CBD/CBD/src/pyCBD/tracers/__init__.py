"""
The tracers module provides an interface for tracing simulation data.
"""
import copy
import time

from pyCBD.tracers.baseTracer import BaseTracer

class Tracers:
	"""
	Collection object for multiple tracers.

	Arguments:
		sim (Simulator):    The CBD simulator of the trace object.

	Note:
		This class will maintain and keep track of the UID of a tracer.
		Don't set this yourself!
	"""
	def __init__(self, sim):
		self.uid = 0
		self.tracers = {}
		self.recovers = {}
		self.bus = []
		self.sim = sim

	def hasTracers(self):
		"""
		Checks that there are registered tracers.
		"""
		return len(self.tracers) == 0

	def thread_loop(self):
		"""
		Mainloop for tracing information. reduces the amount of threads created.
		"""
		while self.sim.is_running():
			while len(self.bus) > 0:
				evt, args = self.bus.pop(0)
				evt(*args)
			time.sleep(0.05)

	def trace(self, event, args):
		"""
		Traces an event.
		Args:
			event (callable):   The event to trace.
			args (iter):        The list of arguments for the event.
		"""
		self.bus.append((event, args))

	def registerTracer(self, tracer, recover=False):
		"""
		Registers a specific tracer to use.

		Args:
			tracer:         Either a tuple of :code:`(file, classname, [args])`,
							similar to `PythonPDEVS <http://msdl.uantwerpen.be/projects/DEVS/PythonPDEVS>`_;
							or an instance of a subclass of :class:`pyCBD.tracers.baseTracer.BaseTracer`.
			recover (bool): Whether or not this is a recovered registration; i.e. whether or not the trace
			                file should be appended. Defaults to :code:`False`.
		"""
		if isinstance(tracer, tuple) and len(tracer) == 3:
			try:
				exec("from pyCBD.tracers.%s import %s" % tracer[:2])
			except:
				exec("from %s import %s" % tracer[:2])
			self.tracers[self.uid] = eval("%s(%i, *%s)" % (tracer[1], self.uid, tracer[2]))
		elif isinstance(tracer, BaseTracer):
			tracer.uid = self.uid
			self.tracers[self.uid] = tracer
		self.recovers[self.uid] = recover
		self.uid += 1

	def deregisterTracer(self, uid):
		"""
		Stops and removes a specific tracer.

		Args:
			uid (int):  The tracer id to stop.
		"""
		if uid in self.tracers:
			self.tracers[uid].stopTracer()
			del self.tracers[uid]

	def startTracers(self, interp=None, model_name="model"):
		"""
		Starts the tracers.

		Args:
			interp (pyCBD.tracers.interpolator.Interpolator):   The interpolator to use for the tracers.
			model_name (str):       The name of the model.

		Returns:

		"""
		for tid in self.tracers:
			self.tracers[tid].setModelName(model_name)
			if interp is not None:
				self.tracers[tid].setInterpolator(copy.deepcopy(interp))
			self.tracers[tid].getInterpolator().set_header(self.sim.model.getAllSignalNames())
			self.tracers[tid].startTracer(self.recovers[tid])

	def stopTracers(self, term_time):
		"""
		Stops all tracers.

		Args:
			term_time (numeric):    The termination time.
		"""
		self.trace(self.traceEndSimulation, (term_time,))
		while len(self.bus) > 0:
			evt, args = self.bus.pop(0)
			evt(*args)
		for tracer in self.tracers.values():
			tracer.stopTracer()

	def getById(self, uid):
		"""
		Obtains a specific tracer.

		Args:
			uid (int):  The tracer id to obtain.

		Raises:
			ValueError: If the tracer does not exist.
		"""
		if uid in self.tracers:
			return self.tracers[uid]
		raise ValueError("No such tracer %d." % uid)

	def traceStartNewIteration(self, curIt, time):
		"""
		Traces a new iteration start.

		Args:
			curIt (int):    The current iteration.
			time (numeric): The current simulation time.
		"""
		for tracer in self.tracers.values():
			tracer.traceStartNewIteration(curIt, time)

	def traceEndNewIteration(self, curIt, time):
		"""
		Traces a new iteration end.

		Args:
			curIt (int):    The current iteration.
			time (numeric): The current simulation time.
		"""
		for tracer in self.tracers.values():
			tracer.traceEndNewIteration(curIt, time)

	def traceCompute(self, curIteration, block):
		"""
		Traces the computation of a specific block.

		Args:
			curIteration (int):         The current iteration.
			block (CBD.Core.BaseBlock): The block for which a compute just happened.
		"""
		for tracer in self.tracers.values():
			tracer.traceCompute(curIteration, block)

	def traceEndSimulation(self, stime):
		"""
		Traces the end of the simulation

		Args:
			stime (numeric):    The final simulation time.
		"""
		for tracer in self.tracers.values():
			tracer.traceEndSimulation(stime)