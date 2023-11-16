"""
This module contains all classes and structures needed for live plotting of data via
polling an object. While specifically made for the CBD simulator, it is independent
of any internal workings.
"""
# import pyCBD.realtime.accurate_time as time
import time
import threading
try:
	import matplotlib
	import matplotlib.pyplot as plt
	import matplotlib.animation as animation
	from matplotlib.patches import Arrow as mplArrow
	_MPL_FOUND = True

	try:
		# Note: Seaborn is built on top of matplotlib
		import seaborn as sns

		_SNS_FOUND = True
	except ImportError:
		_SNS_FOUND = False
except ImportError:
	_MPL_FOUND = False
	_SNS_FOUND = False

try:
	import bokeh.plotting as bkplt
	import bokeh.io
	import bokeh.models
	_BOKEH_FOUND = True
except ImportError:
	_BOKEH_FOUND = False

# __all__ = ['Backend', 'PlotKind', 'PlotHandler', 'PlotManager', 'plot', 'follow', 'set_xlim', 'set_ylim',
#            'Arrow', 'StepPlot', 'ScatterPlot', 'LinePlot']

# TODO: More Plot Kinds

class Backend:
	"""
	In which framework the plots need to be made.

	Note:
		Some attributes won't be available if the corresponding framework is not installed.
	"""
	if _MPL_FOUND:
		MPL         = 1
		""" : : Use `Matplotlib <https://matplotlib.org/>`_."""
		MATPLOTLIB  = 1
		""" : : Use `Matplotlib <https://matplotlib.org/>`_."""

	if _BOKEH_FOUND:
		BKH         = 2
		BOKEH       = 2
		"""
		 : : Use `Bokeh <//docs.bokeh.org/en/latest/index.html>`_.
		
		Important:
			For :code:`BOKEH`, a server must be started with:
	
			.. code-block:: bash
	
			   bokeh serve <experiment file>
			
		Warning:
			Because of how Bokeh works, it is currently impossible to capture premature
			close events on a system. The plots will always remain active once started.
		"""

	if _SNS_FOUND:
		SNS         = 3
		""" : : Use `Seaborn <https://seaborn.pydata.org/>`_."""
		SEABORN     = 3
		""" : : Use `Seaborn <https://seaborn.pydata.org/>`_."""

	@staticmethod
	def exists(value):
		"""
		Checks that a given backend exists.
		"""
		return value in [getattr(Backend, x) for x in dir(Backend) if not x.startswith("_") and \
		                                                                not callable(getattr(Backend, x))]

	@staticmethod
	def compare(name, value):
		"""
		Compares the value against a backend name.

		Args:
			name (str):     The name of the backend to check for.
			value (int):    The value to compare.
		"""
		return name in dir(Backend) and Backend.exists(value) and getattr(Backend, name) == value

	@staticmethod
	def get(name):
		"""
		Gets the backend with a specific name if it exists and if it's installed.

		Args:
			name (str):     The name of the backend to get.
		"""
		return getattr(Backend, name) if name in dir(Backend) else None


class PlotHandler:
	"""
	Handles Real-Time plotting, independent of a plotting framework.

	Every :code:`interval` time, data will be polled from the :code:`object`,
	w.r.t. the given plotting :code:`backend`. The handler will use the knowledge
	of a backend to determine how the given :code:`figure` must be updated.

	This class can be used in any simulation context, where plotting data can be
	polled from an object or a resource.

	Note:
		While technically framework-independent, matplotlib has the least external
		overhead in your code.

	Tip:
		When using multiple plots/plotting instances, you should make use of the
		:class:`PlotManager`.

	Warning:
		Bokeh is still in active development. Not all features will work as required.

	Raises:
		AssertionError: if the backend cannot be located.

	Args:
		object (Any):       The object from which data needs to be polled. By default,
							the :code:`data_xy` attribute will be used on the object,
							which should result in a 2xN array in the form of
							:code:`[[x1, x2, x3...], [y1, y2, y3...]]`. Change this
							behaviour with the :func:`set_data_getter` function.
		figure:             The figure object required for plotting. This has been made
							externally to allow for full manipulation of the plotting
							framework itself. The following explains the axxepted data
							types:

							- **matplotlib:** Tuple (pair) of :code:`(Figure, Axes)`
							- **bokeh:** :code:`Figure`
							- **seaborn:** Tuple (pair) of :code:`(Figure, Axes)`

		kind (PlotKind):    What needs to be plotted. See :class:`PlotKind` for more
							info.
		backend (Backend):  The backend to use for plotting. Defaults to
							:attr:`Backend.MPL` (= matplotlib).
		interval (int):     Amount of milliseconds between plot refreshes.
		frames (int):       The amount of frames for the animation. Only used if the
							animation needs to be saved.
		static (bool):      When :code:`True`, no animation will be created.

	See Also:
		- :class:`Backend`
		- :class:`PlotKind`
		- :class:`PlotManager`
	"""
	def __init__(self, object, figure, kind, backend=Backend.MPL, interval=10, frames=None, static=False):
		assert Backend.exists(backend), "Invalid backend."
		self.object = object
		self.kind = kind
		self.figure = figure
		self.interval = interval

		self.kind._backend = backend
		self.elm = self.kind.create(figure)
		self.__opened = True
		self.__finished = False
		self.__hidden = False

		# obtaining information
		self.__get_data = lambda obj: obj.data_xy
		self.__event_bus = []
		self.__event_thread = threading.Thread(target=self.__event_thread_loop)
		self.__event_thread.start()
		self.__events = {
			"preupdate": [],
			"update": [],
			"closed": []
		}

		# backend info:
		if not static:
			if Backend.compare("MPL", backend) or Backend.compare("SNS", backend):
				self.__ani = animation.FuncAnimation(figure[0], lambda _: self.update(),
				                                     interval=self.interval, frames=frames)
				figure[0].canvas.mpl_connect('close_event', lambda _: self.__close_event())
			elif Backend.compare("BOKEH", backend):
				self.__periodic_callback = bokeh.io.curdoc().add_periodic_callback(lambda: self.update(), interval)
				# No need to do closing callback -- automatically done by simulator

	def signal(self, name, *args):
		"""
		Raise a signal with a specific name and arguments.

		The accepted signals are:

		- :code:`preupdate(data)`: Raised whenever the plot is about to update.
		  It takes the new plot data that has been polled.
		- :code:`update(data)`: Raised whenever the plot updates. It takes the
		  new plot data that has been polled.
		- :code:`closed`: Raised whenever the plot closes. No additional arguments
		  are associated with this event.

		Note:
			Normally, users do not need to call this function.

		Args:
			name (str):     The name of the signal to raise.
			*args:          Additional arguments to pass to the connected events.

		See Also:
			- :func:`PlotHandler.connect`
			- :func:`PlotManager.connect`
			- :func:`follow`
		"""
		if name not in self.__events:
			raise ValueError("Invalid signal '%s' in PlotHandler." % name)
		self.__event_bus.append((name, args))

	def connect(self, name, function):
		"""
		Connect an event with an additional function.
		Useful for e.g. updating the plot axes w.r.t. the data.

		The functions will be called in the order they were connected to the
		events, with the associated arguments. The accepted signals are:

		- :code:`preupdate(data)`: Raised whenever the plot is about to update.
		  It takes the new plot data that has been polled.
		- :code:`update(data)`: Raised whenever the plot updates. It takes the
		  new plot data that has been polled.
		- :code:`closed`: Raised whenever the plot closes. No additional arguments
		  are associated with this event.

		Args:
			name (str):     The name of the signal to raise.
			function:       A function that will be called with the optional arguments
							whenever the event is raised.

		See Also:
			- :func:`PlotHandler.signal`
			- :func:`PlotManager.connect`
			- :func:`follow`
		"""
		if name not in self.__events:
			raise ValueError("Invalid signal '%s' in PlotHandler." % name)
		self.__events[name].append(function)

	def __event_thread_loop(self):
		while not self.__finished:
			while len(self.__event_bus) > 0:
				name, args = self.__event_bus.pop()
				for evt in self.__events[name]:
					evt(*args)
			time.sleep(self.interval / 1000)

	def set_data_getter(self, function):
		"""
		Sets the data getter function call. By default, the :code:`data_xy` attribute
		is polled, but this function provides the flexibility to alter this behaviour.

		Args:
			function:   The function to obtain the data. Takes the :code:`object` as an
						input and should return a 2xN array in the form of
						:code:`[[x1, x2, x3...], [y1, y2, y3...]]`.
		"""
		self.__get_data = function

	def get_data(self):
		"""
		Actually gets the data from the object.
		"""
		return self.__get_data(self.object)

	def get_animation(self):
		"""
		Returns the animation object, if MatPlotLib is used as a backend.
		"""
		return self.__ani

	def close_event(self):
		"""
		Closes the plot/figure associated with this handler.

		See Also:
			:func:`PlotHandler.close_event`
		"""
		if self.kind.is_backend("MPL", "SNS"):
			plt.close(self.figure[0])
		# Make sure we close the plot if the backend fails to do so
		self.__close_event()

	def __close_event(self):
		"""
		Raises the `closed` signal.

		Note:
			This function is only used in the backend to prevent double
			closing of the plots.
		"""
		if self.__opened:
			self.__opened = False
			self.stop()
			self.signal('closed')
			# self.__event_thread.join()

	def is_opened(self):
		"""
		Checks if the plots are still open.
		"""
		return self.__opened

	def update(self):
		"""
		Updates the plot information.
		"""
		# print("update")
		data = self.get_data()
		if not self.__hidden:
			self.signal('preupdate', data)
			res = self.kind.update(self.elm, *data)
			if res is not None:
				self.elm = res
			self.signal('update', data)
		else:
			self.signal('preupdate', data)
			res = self.kind.update(self.elm, [], [])
			if res is not None:
				self.elm = res
			self.signal('update', data)

		if self.__finished:
			self._stop()

	def stop(self):
		"""
		Requests the process to finish polling.
		"""
		self.__finished = True

	def _stop(self):
		"""
		Stops polling for updates, but keeps the plot alive.
		"""
		if self.kind.is_backend("MPL", "SNS"):
			self.__ani.event_source.stop()
		elif self.kind.is_backend("BOKEH"):
			bokeh.io.curdoc().remove_periodic_callback(self.__periodic_callback)

	def terminate(self):
		"""
		Terminate the animation and close the plot.
		"""
		self._stop()
		self.close_event()

	def set_kind_args(self, *args, **kwargs):
		"""
		Sets the (keyword) arguments used for the plot.
		"""
		self.kind.args = args
		self.kind.kwargs = kwargs
		# TODO: pass the args on for the full plot.
		#  Redrawing only changes the x, y coords!

	def hide(self):
		"""
		Hides the plot in the view.

		See Also:
			- :func:`show`
			- :func:`toggle`
		"""
		self.__hidden = True

	def show(self):
		"""
		Shows the plot in the view.

		See Also:
			- :func:`hide`
			- :func:`toggle`
		"""
		self.__hidden = False

	def toggle(self):
		"""
		Toggles between hiding and showing the plot in the view.

		See Also:
			- :func:`hide`
			- :func:`show`
		"""
		self.__hidden = not self.__hidden


def follow(data, size=None, lower_bound=float('-inf'), upper_bound=float('inf'),
           lower_lim=0.0, upper_lim=0.0, perc_keep=0.5):
	"""
	Compute the new limits for the given dataset if the last data point must be followed.
	This is a convenience function for updating the plotting axes' limits. Whenever not
	enough data is available, the axis won't scale down.

	Args:
		data (list):            The data that must be plotted on the axes. Can be a
								shortened version of only the final n values (n > 0).
		size (float):           The total size of the axis to show, even if the data
								did not get there. When :code:`None`, the size is taken
								from the bounds or limits. Defaults to :code:`None`.
		lower_bound (float):    The lower bound of the axis, i.e. the minimal value to
								show, even if the data lies outside of this interval.
								Defaults to :code:`-float('inf')` (-infinity = no limit).
		upper_bound (float):    The upper bound of the axis, i.e. the maximal value to
								show, even if the data lies outside of this interval.
								Defaults to :code:`float('inf')` (infinity = no limit).
		lower_lim (float):      Lowest value to show, even if this value is not reached.
								While :attr:`lower_bound` bounds this point, so no smaller
								values can be shown, :attr:`lower_limit` makes it so this
								valus is always shown, but smaller values may still rescale
								beyond this point. Will be ignored when :attr:`size` is set.
								Defaults to :code:`0.0`.
		upper_lim (float):      Highest value to show, even if this value is not reached.
								While :attr:`upper_bound` bounds this point, so no higher
								values can be shown, :attr:`upper_limit` makes it so this
								valus is always shown, but larger values may still rescale
								beyond this point. Will be ignored when :attr:`size` is set.
								Defaults to :code:`0.0`.
		perc_keep (float):      The percentage at which the final data point must be
								shown. When :code:`0.0`, this point is the lowest value
								shown. When :code:`1.0`, this point is the highest value
								shown. Use this value to change how "centered" the last
								datapoint will be. When the axis grows in a positive
								direction, a value of :code:`0.0` will never show the
								data. When growing negatively, the opposite is true:
								the data will not be shown for a value of :code:`1.0`.
								Defaults to :code:`0.5` (= the middle).

	Warning:
		* The lower bound must be strictly smaller than the upper bound.
		* The size is :code:`None` and the bounds are infinity and the limits are equal.
		* The size cannot be larger than the distance between the bounds.
		* The lower limit must be smaller than (or equal to) the upper limit.

	Examples:
		- Follow a sine wave in the positive-x direction, always keeping a width of 10, in matplotlib.

		.. code-block:: python

			manager = PlotManager()
			manager.register("sin", cbd.find("plot")[0], (fig, ax), LinePlot())
			manager.connect('sin', 'update', lambda d, a=ax: a.set_xlim(follow(d[0], 10.0, lower_bound=0.0)))

		- Follow a sine wave in the negative-x direction, always keeping a width of 10, in matplotlib.

		.. code-block:: python

			manager = PlotManager()
			manager.register("sin", cbd.find("plot")[0], (fig, ax), LinePlot())
			manager.connect('sin', 'update', lambda d, a=ax: a.set_xlim(follow(d[0], 10.0, upper_bound=0.0)))

		- Follow a positive sine-wave, but keep a 10% margin from the right edge of the plot, in matplotlib.

		.. code-block:: python

			manager = PlotManager()
			manager.register("sin", cbd.find("plot")[0], (fig, ax), LinePlot())
			manager.connect('sin', 'update', lambda d, a=ax: a.set_xlim(follow(d[0], 10.0, 0.0, perc_keep=0.9)))
	"""
	if lower_bound >= upper_bound:
		raise ValueError("Lower bound must be strictly smaller than the upper bound.")
	if size is None and (lower_bound == float('-inf') or upper_bound == float('inf')) and lower_lim == upper_lim:
		raise ValueError("When size is unset, the bounds may not be infinity and the limits may not equal each other.")
	if size is not None and upper_bound - lower_bound < size:
		raise ValueError("Invalid size: outside bounds.")
	if lower_lim > upper_lim:
		raise ValueError("Lower limit must be smaller than (or equal to) the upper limit.")

	if size is None:
		if len(data) == 0:
			return lower_lim, upper_lim
		return min(min(data), lower_lim), max(max(data), upper_lim)
	if upper_bound - lower_bound == size:
		return lower_bound, upper_bound
	if len(data) == 0:
		return -size / 2.0, size / 2.0
	value = data[-1]
	low = max(value - size * perc_keep, lower_bound)
	high = min(low + size, upper_bound)
	if high == upper_bound:
		low = high - size
	return low, high


class PlotKind:
	"""
	The kind of plot that needs to be rendered. This class is an abstract superclass.

	Not all backends provide the same functionality for plotting the same shape.
	This class provides a wrapper around all those functionalities to allow for users
	that they only need to change the figure information.

	Args:
		*args:      The arguments to add to the 'shape', excluding the data points.

					.. note::
						The :code:`seaborn` backend does not require any normal args.

		**kwargs:   The keyword arguments to add to the 'shape'.

	See Also:
		- :class:`LinePlot`
		- :class:`StepPlot`
		- :class:`ScatterPlot`
		- Information on the individual plot instances in the corresponding frameworks.
	"""
	def __init__(self, *args, **kwargs):
		self._backend = None
		self.args = args
		self.kwargs = kwargs

	def is_backend(self, *backends):
		"""
		Checks the backend for the plot.
		"""
		for back in backends:
			if Backend.compare(back, self._backend):
				return True
		return False

	def create(self, figure):
		"""
		Called when the figure is first created in the manager.

		Returns:
			The 'shape' information that is created on the plot.
		"""
		raise NotImplementedError()

	def update(self, element, *data):
		"""
		Called when the figure is updated in the manager.

		Args:
			element:    The shape that was returned from the :func:`PlotKind.create`
						method.
			*data:      The data with which to update the plot.
		"""
		raise NotImplementedError()


class LinePlot(PlotKind):
	"""
	Draws a line between all given coordinates.

	Backend Information:
		- **matplotlib:** :func:`matplotlib.axes.Axes.plot`
		- **bokeh:** :func:`bokeh.plotting.Figure.line`
		- **seaborn:** :func:`seaborn.lineplot`
	"""
	def create(self, figure):
		if self.is_backend("MPL"):
			# matplotlib: figure[1] is the axis
			line, = figure[1].plot([], [], *self.args, **self.kwargs)
			return line
		elif self.is_backend("BOKEH"):
			return figure.line([], [], *self.args, **self.kwargs)
		elif self.is_backend("SNS"):
			# matplotlib: figure[1] is the axis
			a = sns.lineplot(x=[0], y=[0], ax=figure[1], **self.kwargs)
			return a.get_lines()[-1]

	def update(self, element, *data):
		if self.is_backend("MPL", "SNS"):
			element.set_data(data[0], data[1])
		elif self.is_backend("BOKEH"):
			element.data_source.data.update(x=data[0], y=data[1])


class StepPlot(PlotKind):
	"""
	Draws a stepped line between all given coordinates.
	See the corresponding backend information to change the step "levels".

	Backend Information:
		- **matplotlib:** :func:`matplotlib.axes.Axes.step`
		- **bokeh:** :func:`bokeh.plotting.Figure.step`
		- **seaborn:** :func:`seaborn.lineplot` with :code:`drawstyle='steps-pre'`
	"""
	def create(self, figure):
		if self.is_backend("MPL"):
			# matplotlib: figure[1] is the axis
			line, = figure[1].step([], [], *self.args, **self.kwargs)
			return line
		elif self.is_backend("BOKEH"):
			return figure.step([], [], *self.args, **self.kwargs)
		elif self.is_backend("SNS"):
			# matplotlib: figure[1] is the axis
			a = sns.lineplot(x=[], y=[], ax=figure[1], drawstyle='steps-pre', **self.kwargs)
			return a.get_lines()[-1]

	def update(self, element, *data):
		if self.is_backend("MPL", "SNS"):
			element.set_data(data[0], data[1])
		elif self.is_backend("BOKEH"):
			element.data_source.data.update(x=data[0], y=data[1])


class ScatterPlot(PlotKind):
	"""
	Draws all given coordinates as points in a 2D space.
	See the corresponding backend information to change the shape of the indicators.

	Backend Information:
		- **matplotlib:** :func:`matplotlib.axes.Axes.scatter`
		- **bokeh:** :func:`bokeh.plotting.Figure.scatter`
		- **seaborn:** :func:`seaborn.scatterplot`
	"""
	def create(self, figure):
		if self.is_backend("MPL"):
			# matplotlib: figure[1] is the axis
			pathc = figure[1].scatter([], [], *self.args, **self.kwargs)
			return pathc
		elif self.is_backend("BOKEH"):
			return figure.scatter([], [], *self.args, **self.kwargs)
		elif self.is_backend("SNS"):
			# matplotlib: figure[1] is the axis
			a = sns.scatterplot(x=[0], y=[0], ax=figure[1], **self.kwargs)
			return a.findobj(matplotlib.collections.PathCollection)[-1]


	def update(self, element, *data):
		if self.is_backend("MPL", "SNS"):
			element.set_offsets(list(zip(*data)))
		elif self.is_backend("BOKEH"):
			element.data_source.data.update(x=data[0], y=data[1])

import math

class Arrow(PlotKind):
	"""
	Draws a "direction" arrow at a position, indicative of an angle.
	This :class:`PlotKind` assumes that the y-component indicates the
	angle.

	Backend Information:
		- **matplotlib:** :func:`matplotlib.axes.Axes.scatter`
		- **bokeh:** Not available.
		- **seaborn:** Not available.
	"""
	def __init__(self, size, position, *args, **kwargs):
		PlotKind.__init__(self, *args, **kwargs)
		self.position = position
		self.size = size

	def create(self, figure):
		x, y = self.position
		if self.is_backend("MPL", "SNS"):
			# matplotlib: figure[1] is the axis
			arrow = mplArrow(x, y, 0, 0, *self.args, **self.kwargs)
			line = figure[1].add_patch(arrow)
			line.set_zorder(20)
			return line
		elif self.is_backend("BKH"):
			arrow = bokeh.models.Arrow(x_start=x, y_start=y, x_end=x, y_end=y, **self.kwargs)
			figure.add_layout(arrow)
			return arrow

	def update(self, element, *data):
		heading = data[1]
		dx = math.cos(heading[-1]) * self.size
		dy = math.sin(heading[-1]) * self.size
		x, y = self.position

		if self.is_backend("MPL", "SNS"):
			ax = element.axes
			element.remove()
			arrow = mplArrow(x, y, dx, dy, *self.args, **self.kwargs)
			line = ax.add_patch(arrow)
			line.set_zorder(20)
			return line
		elif self.is_backend("BKH"):
			element.x_start = x
			element.y_start = y
			element.x_end = x + dx
			element.y_end = y + dy
			return element


class PlotManager:
	"""
	Manages multiple :class:`PlotHandler` instances.
	Use this class as a centralized unit to manage one or more plots in the system.

	Args:
		backend (Backend):  The backend to use.

	Raises:
		AssertionError: if the backend cannot be located.

	See Also:
		- :class:`Backend`
		- :class:`PlotHandler`
	"""
	def __init__(self, backend=Backend.get("MPL")):
		assert Backend.exists(backend), "Invalid backend."
		self.__handlers = {}
		self.backend = backend

	def is_opened(self):
		"""
		Checks if there is at least a single plot left open.
		"""
		return any([h.is_opened() for h in self.__handlers.values()])

	def all_opened(self):
		"""
		Checks if all plots are still open.
		"""
		return all([h.is_opened() for h in self.__handlers.values()])

	def register(self, name, object, figure, kind, **kwargs):
		"""
		Register a single :class:`PlotHandler` to plot information.

		Args:
			name (str):         The name for this handler. Will be used to optionally
								access it afterwards.
			object (Any):       The object from which data needs to be polled. By default,
								the :code:`data_xy` attribute will be used on the object,
								which should result in a 2xN array in the form of
								:code:`([x1, x2, x3...], [y1, y2, y3...])`.
			figure:             The figure object required for plotting. This has been made
								externally to allow for full manipulation of the plotting
								framework itself.
			kind (PlotKind):    What needs to be plotted. See :class:`PlotKind` for more
								info.
			**kwargs:           Additional arguments to pass to the :class:`PlotHandler`
								constructor.

		See Also:
			:class:`PlotHandler`
		"""
		if name in self.__handlers:
			raise ValueError("PlotManager: PlotHandler '%s' already registered." % name)
		self.__handlers[name] = PlotHandler(object, figure, kind, self.backend, **kwargs)

	def unregister(self, name):
		"""
		Removes a single :class:`PlotHandler` from the manager.

		Args:
			name (str): The identifying name for the handler.
		"""
		h = self.get(name)
		h.close_event()
		del self.__handlers[name]

	def get(self, name):
		"""
		Obtains a single :class:`PlotHandler`, given its name.

		Args:
			name (str): The identifying name for the handler to obtain.
		"""
		if name not in self.__handlers:
			raise ValueError("PlotManager: No PlotHandler exists with name '%s'." % name)
		return self.__handlers[name]

	def connect(self, handler_name, event_name, function):
		"""
		Connect an event to a specific handler.

		Args:
			handler_name (str): The identifying name for the handler.
			event_name (str):   The name for the event.
			function:           A function to execute whenever the event is raised.

		See Also:
			- :func:`PlotHandler.connect`
			- :func:`PlotHandler.signal`
		"""
		self.get(handler_name).connect(event_name, function)

	def terminate(self):
		"""
		Forcibly terminate the manager and all its handlers.
		"""
		for handler in self.__handlers.values():
			handler.terminate()

	def stop(self):
		"""
		Stop polling for all updates.
		"""
		for handler in self.__handlers.values():
			handler.stop()

	def set_xlim(self, figure, values):
		"""
		Shorthand method for setting the x limits of the figure.

		Warning:
			Bokeh requires this method to be called in a "clean" tick. Call
			:meth:`bokeh_set_xlim` instead.

		Args:
			figure:             The figure to alter.
			values (tuple):     The new limits for the x-axis.
		"""
		backend = self.backend
		if Backend.compare("MPL", backend) or Backend.compare("SNS", backend):
			figure[1].set_xlim(values)
		elif Backend.compare("BKH", backend):
			lower, upper = values
			figure.x_range.start = lower
			figure.x_range.end = upper

	def set_ylim(self, figure, values):
		"""
		Shorthand method for setting the y limits of the figure.

		Warning:
			Bokeh requires this method to be called in a "clean" tick. Call
			:meth:`bokeh_set_ylim` instead.

		Args:
			figure:             The figure to alter.
			values (tuple):     The new limits for the y-axis.
		"""
		backend = self.backend
		if Backend.compare("MPL", backend) or Backend.compare("SNS"):
			figure[1].set_ylim(values)
		elif Backend.compare("BKH", backend):
			lower, upper = values
			figure.y_range.start = lower
			figure.y_range.end = upper

	if _BOKEH_FOUND:
		def bokeh_set_xlim(self, figure, doc, values):
			"""
			Helper function to set the x limits in Bokeh, as it should be called in a "safe" tick.

			Args:
				figure:     The figure to set the x limits for.
				doc:        The Bokeh document to which the figure belongs.
				values:     The new x limits.
			"""
			assert Backend.compare("BKH", self.backend), "Can only be called for a Bokeh backend!"
			doc.add_next_tick_callback(lambda lim=values: self.set_xlim(figure, lim))

		def bokeh_set_ylim(self, figure, doc, values):
			"""
			Helper function to set the y limits in Bokeh, as it should be called in a "safe" tick.

			Args:
				figure:     The figure to set the y limits for.
				doc:        The Bokeh document to which the figure belongs.
				values:     The new y limits.
			"""
			assert Backend.compare("BKH", self.backend), "Can only be called for a Bokeh backend!"
			doc.add_next_tick_callback(lambda lim=values: self.set_ylim(figure, lim))


def plot(object, figure, kind, backend=Backend.get("MPL"), margin=(0.02, 0.02)):
	"""
	Plot data on a figure after the simulation has finished.
	This will automatically plot the full graph, so all axis scaling needs to be done afterwards.

	Args:
		object (Any):       The object from which data needs to be polled. By default,
							the :code:`data_xy` attribute will be used on the object,
							which should result in a 2xN array in the form of
							:code:`([x1, x2, x3...], [y1, y2, y3...])`.
		figure:             The figure object required for plotting. This has been made
							externally to allow for full manipulation of the plotting
							framework itself.
		kind (PlotKind):    What needs to be plotted. See :class:`PlotKind` for more
							info.
		backend (Backend):  The backend to use.
		margin (tuple):     A margin for the limits of the axes.

	See Also:
		:class:`PlotHandler`
	"""
	assert Backend.exists(backend), "Invalid backend."
	ph = PlotHandler(object, figure, kind, backend, static=True)
	ph.update()

	x, y = ph.get_data()
	xlim = min(x), max(x)
	ylim = min(y), max(y)
	xlim = xlim[0] - margin[0], xlim[1] + margin[0]
	ylim = ylim[0] - margin[1], ylim[1] + margin[1]

	set_xlim(figure, backend, xlim)
	set_ylim(figure, backend, ylim)
