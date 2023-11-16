import logging
import threading

from pyCBD.Core import Port
from pyCBD.depGraph import createDepGraph
from pyCBD.loopsolvers.linearsolver import LinearSolver
from pyCBD.realtime.threadingBackend import ThreadingBackend, Platform
from pyCBD.scheduling import TopologicalScheduler
from pyCBD.tracers import Tracers
from pyCBD.tracers.interpolator import Interpolator
from pyCBD.state_events.locators import RegulaFalsiStateEventLocator
import pyCBD.realtime.accurate_time as time

_TQDM_FOUND = True
try:
	from tqdm import tqdm
except ImportError:
	_TQDM_FOUND = False


class Simulator:
	"""
	Simulator for a CBD model. Allows for execution of the simulation.
	This class implements the semantics of CBDs.

	Args:
		model (CBD.Core.CBD):    A :class:`CBD` model to simulate.

	:Defaults:
		The following properties further define the internal mechanisms of
		the simulator. As a handy look-up table, all defaults are listed
		in the table below. Take a look at the :code:`See Also` column for
		more info on the property.

	.. list-table::
	   :widths: 20 40 40
	   :header-rows: 1

	   * - Property
	     - Default
	     - See Also
	   * - real-time?
	     - :code:`False`
	     - :func:`setRealTime`
	   * - real-time scale
	     - 1.0
	     - :func:`setRealTime`
	   * - termination time
	     - :code:`float('inf')`
	     - :func:`setTerminationTime`
	   * - termination condition
	     - :code:`None`
	     - :func:`setTerminationCondition`
	   * - scheduler
	     - :class:`pyCBD.scheduling.TopologicalScheduler`
	     - :func:`setScheduler`
	   * - threading platform (subsystem)
	     - :class:`pyCBD.realtime.threadingPython.threadingPython`
	     - :func:`setRealTimePlatform`, :func:`setRealTimePlatformThreading`,
	       :func:`setRealTimePlatformTk`, :func:`setRealTimePlatformGameLoop`
	   * - progress bar?
	     - :code:`False`
	     - :func:`setProgressBar`
	   * - strong component system solver
	     - :class:`pyCBD.linearsolver.LinearSolver`
	     - :func:`setAlgebraicLoopSolver`
	   * - state event locator
	     - :class:`pyCBD.state_events.locators.RegulaFalsiStateEventLocator`
	     - :func:`setStateEventLocator`
	"""
	def __init__(self, model):
		self.model = model

		self.__deltaT = 1.0
		self.__communication_interval = None
		self.__realtime = False
		self.__finished = True
		self.__stop_requested = False

		# scale of time in the simulation.
		self.__realtime_scale = 1.0
		# maximal amount of events with delay 0
		self.__realtime_counter_max = 100
		# current amount of events
		self.__realtime_counter = self.__realtime_counter_max
		# Starting time of the simulation
		self.__realtime_start_time = 0.0

		self.__termination_time = float('inf')
		self.__termination_condition = None

		# simulation data [dep graph, strong components, curIt]
		self.__sim_data = [None, None, 0]

		self.__scheduler = TopologicalScheduler()

		self.__threading_backend = None
		self.__threading_backend_subsystem = Platform.PYTHON
		self.__threading_backend_args = []

		self.__progress = False
		self.__progress_event = None
		self.__progress_finished = True
		self.__logger = logging.getLogger("CBD")
		self.__tracer = Tracers(self)

		self.__lasttime = None

		self.__event_bus = []
		self.__events = {
			"started": [],
			"finished": [],
			"prestep": [],
			"poststep": [],
			"clock_update": []
		}

		self.__state_events = []
		self.__stel = None
		self.setStateEventLocator(RegulaFalsiStateEventLocator())
		
		# TODO: make this variable, given more solver implementations
		# self.__solver = SympySolver(self.__logger)
		self.__solver = LinearSolver(self.__logger)

	def run(self, term_time=None):
		"""
		Simulates the model.

		Args:
			term_time (float):  When not :code:`None`, overwrites the termination time
								with the new value. This value will be accurate upto 8
								decimal points.
		"""
		self.__finished = False
		self.__stop_requested = False
		if term_time is not None:
			self.__termination_time = term_time

		if self.getClock() is None:
			self.model.addFixedRateClock(self.model.getUniqueBlockName("clock"), self.__deltaT)

		interp = None
		if self.__communication_interval is not None:
			interp = Interpolator(ci=self.__communication_interval, start_time=self.getClock().getStartTime())
		self.__tracer.startTracers(interp, self.model.getBlockName())
		self.__sim_data = [None, None, 0]
		self.__progress_finished = False
		if self.__threading_backend is None:
			# If there is still a backend, it is the same, so keep it!
			self.__threading_backend = ThreadingBackend(self.__threading_backend_subsystem,
		                                                self.__threading_backend_args)

		if _TQDM_FOUND and self.__progress and self.__termination_time < float('inf'):
			# Setup progress bar if possible
			thread = threading.Thread(target=self.__progress_update)
			thread.daemon = True
			thread.start()

		if self.__realtime:
			self.__realtime_start_time = time.time()
			self.__lasttime = 0.0

		self.__threading_backend.run_on_new_thread(self.__tracer.thread_loop)
		self.__threading_backend.run_on_new_thread(self.__event_thread_loop)
		self.signal("started")
		if self.__realtime:
			# Force execute the first iteration now. This way iteration n (n > 0) is
			# computed before the real-time is at time n. This allows the computation
			# of exact LCC (and possible rewinds) before the real-time clock is at that
			# point.
			# TODO: Maybe only do this if there are LCC to be checked?
			#       There is no other reason to "run" earlier than required.
			self._do_single_step()
			self.__threading_backend.wait(0.0, self.__runsim)
		else:
			self.__runsim()

	def __finish(self):
		"""
		Terminate the simulation.
		"""
		if not self.__progress:
			# Whenever the progress bar is initialized, wait until it ends
			self.__progress_finished = True
		self.__tracer.stopTracers(self.getTime())
		self.signal("finished")
		self.__finished = True

		# Make sure all events are executed
		self.__threading_backend.wait(0.0, lambda: self.__event_thread_loop(10))

	def __check(self):
		"""
		Checks if the simulation still needs to continue.
		This is done based on the termination time and condition.

		Returns:
			:code:`True` if the simulation needs to be terminated and
			:code:`False` otherwise.
		"""
		ret = self.__stop_requested
		if self.__termination_condition is not None:
			ret = ret or self.__termination_condition(self.model, self.__sim_data[2])
		return ret or round(abs(self.__termination_time - self.getTime()), 8) < self.getDeltaT()

	def stop(self):
		"""
		Requests a termination of the current running simulation.
		"""
		self.__stop_requested = True

	def is_running(self):
		"""
		Returns :code:`True` as long as the simulation is running.
		This is a convenience function to keep real-time simulations
		alive, or to interact from external sources.
		"""
		return not self.__progress_finished and not self.__finished

	def getClock(self):
		"""
		Gets the simulation clock.

		See Also:
			- :func:`getTime`
			- :func:`getRelativeTime`
			- :func:`getDeltaT`
			- :func:`setDeltaT`
			- :class:`pyCBD.lib.std.Clock`
		"""
		return self.model.getClock()

	def getTime(self):
		"""
		Gets the current simulation time.

		See Also:
			- :func:`getClock`
			- :func:`getRelativeTime`
			- :func:`getDeltaT`
			- :func:`setDeltaT`
			- :class:`pyCBD.lib.std.Clock`
		"""
		return self.getClock().getTime(self.__sim_data[2])

	def getRelativeTime(self):
		"""
		Gets the current simulation time, ignoring a starting offset.

		See Also:
			- :func:`getClock`
			- :func:`getTime`
			- :func:`getDeltaT`
			- :func:`setDeltaT`
			- :class:`pyCBD.lib.std.Clock`
		"""
		return self.getClock().getRelativeTime(self.__sim_data[2])

	def getDeltaT(self):
		"""
		Gets the delta in-between iteration steps.

		See Also:
			- :func:`getClock`
			- :func:`getTime`
			- :func:`getRelativeTime`
			- :func:`setDeltaT`
			- :class:`pyCBD.lib.std.Clock`
		"""
		return self.getClock().getDeltaT()

	def setDeltaT(self, delta_t):
		"""
		Sets the delta in-between iteration steps.

		Args:
			delta_t (float):    The delta.

		Note:
			If the model has a :class:`pyCBD.lib.std.Clock` block instance, calling
			this function will have no effect. It is merely meant to be used for
			fixed step simulations.

		Note:
			While unnecessary, this function is kept for backwards compatibility.

		See Also:
			- :func:`getClock`
			- :func:`getTime`
			- :func:`getRelativeTime`
			- :func:`getDeltaT`
			- :class:`pyCBD.lib.std.Clock`
			- :func:`setCommunicationInterval`
			- :func:`setStepSize`
		"""
		self.__deltaT = delta_t

	def setCommunicationInterval(self, delta):
		"""
		Sets the time delta at which the information is communicated to the user.
		When :code:`None`, the integration interval (i.e., delta t) will be used
		for this.

		Args:
			delta (float):  The delta. When :code:`None`, this value will be unset.

		Note:
			This function will only influence the tracers that make use of this
			feature. This has to do with what is communicated to the user and
			not to when the actual computations happen.

		.. versionadded:: 1.6

		See Also:
			- :func:`getClock`
			- :func:`getTime`
			- :func:`getRelativeTime`
			- :func:`getDeltaT`
			- :func:`setDeltaT`
			- :class:`pyCBD.lib.std.Clock`
			- :func:`setStepSize`
		"""
		self.__communication_interval = delta

	def setScheduler(self, scheduler):
		"""
		Sets the scheduler for the simulation. It will identify the
		order of the components in a computation.

		Args:
			scheduler (CBD.scheduling.Scheduler):   The scheduler to use.
		"""
		self.__scheduler = scheduler

	def setAlgebraicLoopSolver(self, solver):
		"""
		Sets the algebraic loop solver for the simulation. It will identify the
		order of the components in a computation.

		Args:
			solver (CBD.loopsolvers.solver.Solver):   The loop solver to use.
		"""
		self.__solver = solver

	def setStateEventLocator(self, stel):
		"""
		Sets the state event locator to use when level crossings occur.

		Args:
			stel (CBD.state_events.locators.StateEventLocator): The new state event to use.
		"""
		self.__stel = stel
		self.__stel.setSimulator(self)

	def registerStateEvent(self, event):
		"""
		Registers a state event to the current simulator.

		Args:
			event (CBD.state_events.StateEvent):    The event to register.
		"""
		self.__state_events.append(event)

	def setBlockRate(self, block_path, rate):
		"""
		Sets the rate for a specific block. Independent of the stepsize, the
		rate will identify that a certain block must only execute every
		:code:`r` time.

		Note:
			Blocks for which no rate has been set will always be computed.

		Args:
			block_path (str):   The path of the block to set a rate of.
			rate (float):       The rate of the block.
		"""
		self.__scheduler.setRate(block_path, rate)

	def setRealTime(self, enabled=True, scale=1.0):
		"""
		Makes the simulation run in (scaled) real time.

		Args:
			enabled (bool): When :code:`True`, realtime simulation will be enabled.
							Otherwise, it will be disabled. Defaults to :code:`True`.
			scale (float):  Optional scaling for the simulation time. When greater
							than 1, the simulation will run slower than the actual
							time. When < 1, it will run faster.
							E.g. :code:`scale = 2.0` will run twice as long.
							Defaults to :code:`1.0`.
		"""
		self.__realtime = enabled
		# Scale of 2 => twice as long
		self.__realtime_scale = scale

	def setProgressBar(self, enabled=True):
		"""
		Uses the `tqdm <https://tqdm.github.io/>`_ package to display a progress bar
		of the simulation.

		Args:
			enabled (bool): Whether or not to enable/disable the progress bar.
							Defaults to :code:`True` (= show progress bar).

		Note:
			A progressbar hijacks printing to the console, hence no output shall be
			shown.

		Raises:
			AssertionError: if the :code:`tqdm` module cannot be located.
		"""
		assert _TQDM_FOUND, "Module tqdm not found. Progressbar is not possible."
		self.__progress = enabled

	def setTerminationCondition(self, func):
		"""
		Sets the system's termination condition.

		Args:
			func:   A function that takes the model and the current iteration as input
					and produces :code:`True` if the simulation needs to terminate.

		Note:
			When set, the progress bars (see :func:`setProgressBar`) may not work as intended.

		See Also:
			:func:`setTerminationTime`
		"""
		# TODO: allow termination condition to set progressbar update value?
		self.__termination_condition = func

	def setTerminationTime(self, term_time):
		"""
		Sets the termination time of the system.

		Note:
			This is accurate upto 8 decimal points.

		Args:
			term_time (float):  Termination time for the simulation.
		"""
		self.__termination_time = term_time

	def setRealTimePlatform(self, subsystem, *args):
		"""
		Sets the realtime platform to a platform of choice.
		This allows more complex/efficient simulations.

		Calling this function automatically sets the simulation to realtime.

		Args:
			subsystem (Platform):   The platform to use.
			args:                   Optional arguments for this platform.
									Currently, only the TkInter platform
									makes use of these arguments.

		Note:
			To prevent misuse of the function, please use one of the wrapper
			functions when you have no idea what you're doing.

		See Also:
			- :func:`setRealTimePlatformThreading`
			- :func:`setRealTimePlatformTk`
			- :func:`setRealTimePlatformGameLoop`
		"""
		self.setRealTime(True)
		self.__threading_backend = None
		self.__threading_backend_subsystem = subsystem
		self.__threading_backend_args = args

	def setRealTimePlatformThreading(self):
		"""
		Wrapper around the :func:`setRealTimePlatform` call to automatically
		set the Python Threading backend.

		Calling this function automatically sets the simulation to realtime.

		See Also:
			- :func:`setRealTimePlatform`
			- :func:`setRealTimePlatformTk`
			- :func:`setRealTimePlatformGameLoop`
		"""
		self.setRealTimePlatform(Platform.THREADING)

	def setRealTimePlatformGameLoop(self):
		"""
		Wrapper around the :func:`setRealTimePlatform` call to automatically
		set the Game Loop backend. Using this backend, it is expected the user
		will periodically call the :func:`realtime_gameloop_call` method to
		update the simulation step. Timing is still maintained internally.

		Calling this function automatically sets the simulation to realtime.

		See Also:
			- :func:`setRealTimePlatform`
			- :func:`setRealTimePlatformThreading`
			- :func:`setRealTimePlatformTk`
			- :func:`realtime_gameloop_call`
			- :doc:`examples/RealTime`
		"""
		self.setRealTimePlatform(Platform.GAMELOOP)

	def setRealTimePlatformTk(self, root):
		"""
		Wrapper around the :func:`setRealTimePlatform` call to automatically
		set the TkInter backend.

		Calling this function automatically sets the simulation to realtime.

		Args:
			root:   TkInter root window object (tkinter.Tk)

		See Also:
			- :func:`setRealTimePlatform`
			- :func:`setRealTimePlatformThreading`
			- :func:`setRealTimePlatformGameLoop`
		"""
		self.setRealTimePlatform(Platform.TKINTER, root)

	def realtime_gameloop_call(self, time=None):
		"""
		Do a step in the realtime-gameloop platform.

		Args:
			time (float):   Simulation time to be passed on. Only to be used
							for the alternative gameloop backend.

		Note:
			This function will only work for a :attr:`Platform.GAMELOOP` or a
			:attr:`Platform.GLA` simulation, after the :func:`run` method has
			been called.

		See Also:
			- :func:`setRealTimePlatform`
			- :func:`setRealTimePlatformGameLoop`
			- :func:`run`
		"""
		self.__threading_backend.step(time)

	def _do_single_step(self):
		"""
		Does a single simulation step.

		Warning:
			Do **not** use this function to forcefully progress the simulation!
			All functionalities for validly simulating and executing a system
			that are provided through other parts of the interface should be
			sufficient to do a viable simulation. This function should only be
			used by the inner workings of the simulator and its functional parts.
		"""
		pre = time.time()
		simT = self.getTime()
		self.signal("prestep", pre, simT)
		curIt = self.__sim_data[2]
		self.__tracer.trace(self.__tracer.traceStartNewIteration, (curIt, simT))

		# Efficiency reasons: dep graph only changes at these times
		#   in the given set of library blocks.
		# TODO: Must be set to "every time" instead.
		if curIt < 2 or self.__sim_data[0] is None:
			self.__sim_data[0] = createDepGraph(self.model, curIt)
		self.__sim_data[1] = self.__scheduler.obtain(self.__sim_data[0], curIt, simT)
		self._lcc_compute()

		# State Event Location
		lcc = float('inf')
		lcc_evt = None
		for event in self.__state_events:
			if not event.fired and self.__stel.detect_signal(event.output_name, event.level, event.direction):
				event.fired = True
				t = self.__stel.run(event.output_name, event.level, event.direction)

				lcc_evt = event
				lcc = min(lcc, t)
			elif event.fired:
				event.fired = False

		if lcc != float('inf'):
			# TODO: Ideally, the model was cached here and should not be recomputed
			self.__stel._function(lcc_evt.output_name, lcc, lcc_evt.level, noop=False)

			lcc_evt.event(lcc_evt, lcc, self.model)

			# reset to allow for new IC computation
			self.model.clearSignals()
			self.model.getClock().setStartTime(lcc)
			self.model.getClock().reset()
			self.__sim_data[0] = None
			self.__sim_data[2] = 0
		post = time.time()
		self.__tracer.trace(self.__tracer.traceEndNewIteration, (curIt, simT))
		self.signal("poststep", pre, post, self.getTime())

	def _lcc_compute(self):
		"""
		Computes the blocks at the current time and increases the iteration counter.
		Mainly used inside of Level Crossing Detection, hence the name.
		"""
		self.__computeBlocks(self.__sim_data[1], self.__sim_data[0], self.__sim_data[2])
		self.__sim_data[2] += 1

	def _rewind(self):
		"""
		Rewinds the simulator to the previous iteration.
		"""
		self.__sim_data[2] -= 1
		self.model._rewind()

	def __realtimeWait(self):
		"""
		Wait until next realtime event.

		Returns:
			:code:`True` if a simulation stop is required and
			:code:`False` otherwise.
		"""
		current_time = time.time() - self.__realtime_start_time
		next_sim_time = min(self.__termination_time, self.__lasttime + self.getDeltaT())

		# Scaled Time
		next_sim_time *= self.__realtime_scale

		# Subtract the time that we already did our computation
		wait_time = next_sim_time - current_time
		self.__lasttime = next_sim_time / self.__realtime_scale

		if wait_time <= 0.0:
			# event is overdue => force execute
			self.__realtime_counter -= 1
			if self.__realtime_counter < 0:
				# Too many overdue events at a time
				self.__realtime_counter = self.__realtime_counter_max
				self.__threading_backend.wait(0.01, self.__runsim)
				return True
			return False

		self.__realtime_counter = self.__realtime_counter_max
		self.__threading_backend.wait(wait_time, self.__runsim)
		return True

	def __runsim(self):
		"""
		Do the actual simulation.
		"""
		self.__realtime_counter = self.__realtime_counter_max
		while True:
			# Force terminate when the main thread is not active anymore
			#   There is no need to keep the simulation alive in this case
			if not self.__threading_backend.is_alive() or self.__check():
				self.__finish()
				break

			self._do_single_step()

			if self.__threading_backend_subsystem == Platform.GLA:
				self.__threading_backend.wait(self.getDeltaT(), self.__runsim)
				break

			if self.__realtime and self.__realtimeWait():
				# Next event has been scheduled, kill this process
				break

	def __computeBlocks(self, sortedGraph, depGraph, curIteration):
		"""
		Compute the new state of the model.

		Args:
			sortedGraph:        The set of strong components.
			depGraph:           A dependency graph.
			curIteration (int): Current simulation iteration.
		"""
		for component in sortedGraph:
			if not self.__hasCycle(component, depGraph):
				block = component[0]  # the strongly connected component has a single element
				if isinstance(block, Port):
					continue
				if curIteration == 0 or self.__scheduler.mustCompute(block, self.getTime()):
					block.compute(curIteration)
					self.__tracer.trace(self.__tracer.traceCompute, (curIteration, block))
			else:
				# Detected a strongly connected component
				self.__solver.checkValidity(self.model.getPath(), component)
				solverInput = self.__solver.constructInput(component, curIteration)
				solutionVector = self.__solver.solve(solverInput)
				for block in component:
					if curIteration == 0 or self.__scheduler.mustCompute(block, self.getTime()):
						blockIndex = component.index(block)
						block.appendToSignal(solutionVector[blockIndex])
						self.__tracer.trace(self.__tracer.traceCompute, (curIteration, block))
		self.__tracer.trace(self.__tracer.traceCompute, (curIteration, self.model))

	def __hasCycle(self, component, depGraph):
		"""
		Determine whether a component is cyclic or not.

		Args:
			component (list):   The set of strong components.
			depGraph:           The dependency graph.
		"""
		assert len(component) >= 1, "A component should have at least one element"
		if len(component) > 1:
			return True
		# a strong component of size one may still have a cycle: a self-loop
		return depGraph.hasDependency(component[0], component[0])

	def __progress_update(self):
		"""
		Updates the progress bar.
		"""
		assert _TQDM_FOUND, "Module tqdm not found. Progressbar is not possible."
		end = self.__termination_time
		pbar = tqdm(total=end, bar_format='{desc}: {percentage:3.0f}%|{bar}| {n:.2f}/{total_fmt} '
		                                  '[{elapsed}/{remaining}, {rate_fmt}{postfix}]')
		last = 0.0
		while not self.__finished:
			now = self.getTime()
			# print(end, now, last)
			pbar.update(min(now, end) - last)
			last = now
			time.sleep(0.5)     # Only update every half a second
		if last < end:
			pbar.update(end - last)
		pbar.close()
		# TODO: prints immediately after break pbar...
		self.__progress_finished = True

	def connect(self, name, function):
		"""
		Connect an event with an additional, user-defined function. These functions
		will be executed on a separate thread and polled every 50 milliseconds.

		Warning:
			It is expected that the passed function terminates at a certain point
			in time, to prevent an infinitely running process.

		Warning:
			There is no guarantee that these functions will be executed in-order of
			connection. For safety, it is best to see these events as not thread-safe.

		The functions will be called in the order they were connected to the
		events, with the associated arguments. The accepted signals are:

		- :code:`started`:              Raised whenever the simulation setup has completed,
										but before the actual simulation begins.
		- :code:`finished`:             Raised whenever the simulation finishes.
		- :code:`prestep(t, st)`:       Raised before a step is done. :code:`t` is the real
										time before the step and :code:`st` is the simulation
										time.
		- :code:`poststep(o, t, st)`:   Raised after a step is done. :code:`o` is the real
										time before the step, :code:`t` is the real time after
										the step and :code:`st` is the simulation time of the
										step.
		- :code:`clock_update(delta)`:  Raised whenever the clock updates. It takes the (new)
										delta for the simulation.

		Args:
			name (str):     The name of the signal to raise.
			function:       A function that will be called with the optional arguments
							whenever the event is raised.
		"""
		if name not in self.__events:
			raise ValueError("Invalid signal '%s' in Simulator." % name)
		self.__events[name].append(function)

	def signal(self, name, *args):
		"""
		Raise a signal with a specific name and arguments.

		The accepted signals are:

		- :code:`started`:              Raised whenever the simulation setup has
										completed, but before the actual simulation
										begins.
		- :code:`finished`:             Raised whenever the simulation finishes.
		- :code:`prestep`:              Raised before a step is done.
		- :code:`poststep`:             Raised after a step is done.
		- :code:`clock_update(delta)`:  Raised whenever the clock updates. It takes
										the (new) delta for the simulation.

		Note:
			Normally, users do not need to call this function.

		Args:
			name (str):     The name of the signal to raise.
			*args:          Additional arguments to pass to the connected events.

		See Also:
			:func:`connect`
		"""
		if name not in self.__events:
			raise ValueError("Invalid signal '%s' in Simulator." % name)
		self.__event_bus.append((name, args))

	def __event_thread_loop(self, cnt=-1):
		i = 0
		while (not self.__finished or len(self.__event_bus) > 0) and (cnt == -1 or cnt <= i):
			i += 1
			if len(self.__event_bus) > 0:
				name, args = self.__event_bus.pop()
				for evt in self.__events[name]:
					evt(*args)
			time.sleep(0.05)

	def setCustomTracer(self, *tracer):
		"""
		Sets a custom tracer.

		Args:
			*tracer:    Either a single instance of a subclass of
						:class:`pyCBD.tracers.baseTracer.BaseTracer` or three elements
						:code:`filename` (str), :code:`classname` (str) and
						:code:`args` (tuple) to allow instantiation similar to
						`PythonPDEVS <http://msdl.cs.mcgill.ca/projects/DEVS/PythonPDEVS>`_.

		Note:
			Calling this function multiple times with the same arguments will continuously add
			new tracers. Thus output to multiple files is possible, though more inefficient than
			simply (manually) copying the file at the end.
		"""
		if len(tracer) == 1:
			self.__tracer.registerTracer(tracer[0])
		elif len(tracer) == 3:
			self.__tracer.registerTracer(tracer)
		else:
			raise ValueError("Invalid amount of arguments for custom tracer.")

	def setVerbose(self, filename=None):
		"""
		Sets the verbose tracer.

		Args:
			filename (Union[str, None]):    The file to which the trace must be written.
											When :code:`None`, the trace will be written to
											the console.

		Note:
			Calling this function multiple times will continuously add new tracers. Thus output
			to multiple files is possible, though more inefficient than simply (manually) copying
			the file at the end.

		Warning:
			Using multiple verbose tracers with the same filename will yield errors and undefined
			behaviour.
		"""
		self.setCustomTracer("tracerVerbose", "VerboseTracer", (filename,))
