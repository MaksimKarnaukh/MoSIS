"""
This file contains all classes to help schedule the CBD simulator
at every iteration/time.
"""
from math import *

class Scheduler:
	"""
	Identifies an order in which the dependency graph must be traversed/computed.

	Warning:
		This class is a semi-virtual parent class of all schedulers. Therefore, only
		subclasses should be used.

	Note:
		When creating a custom scheduler (i.e. by subclassing), care must be taken to
		ensure all strongly connected components are grouped together!

	Args:
		recompute_at (iter):    An iterable of numeric values, identifying the iterations at
								which the schedule must be recomputed. When :code:`True`,
								the schedule will be recomputed every time. Defaults to
								:code:`(0, 1)` (i.e. only at simulation start and iteration 1).
		rates (dict):           A dictionary of :code:`block path -> rate`; indentifying how often
								they should fire. The rate is a float, which will be compared
								against the time. :code:`None` identifies the empty dictionary.
	"""
	def __init__(self, recompute_at=(0, 1), rates=None):
		self.recompte_at = recompute_at
		self.rates = {} if rates is None else rates
		self.__last_schedule = None

	# def getNextActionDelta(self, time, dt):
	# 	"""
	# 	Helps in identifying if a new action is scheduled in the near future.
	#
	# 	Args:
	# 		time (float):   The current simulation time.
	# 		dt (float):     The next delta t as defined/computed by the simulator.
	#
	# 	Returns:
	# 		The next time when something must happen.
	# 	"""
	# 	next = time + dt
	# 	for rate in self.rates.values():
	# 		d = ceil(time / rate) * rate
	# 		if abs(d - time) < 1e-6:
	# 			continue
	# 		next = min(next, d)
	# 	return next - time

	def mustCompute(self, block, time):
		"""
		Checks if the block must be computed.

		Args:
			block (CBD.Core.BaseBlock): The block that must be checked.
			time (float):               The time at which the computation must occur.
		"""
		name = block.getPath()
		if name not in self.rates:
			return True
		rate = self.rates[name]
		d = ceil(time / rate) * rate
		return abs(d - time) < 1e-6

	def setRate(self, block_name, rate):
		"""
		Sets a specific rate for a block. If no rate has been set, it will be assumed the
		block will be executed every iteration. If a rate was already set for the block,
		calling this function will overwrite its previous value.

		Args:
			block_name (str):   The name of the block to set the rate of.
			rate (float):       The interval of **time** at which the block must be executed.
		"""
		self.rates[block_name] = rate

	def obtain(self, depGraph, curIt, time):
		"""
		Obtains the schedule at a specific iteration/time, optionally recomputing
		the value if required.

		Args:
			depGraph (CBD.depGraph.DepGraph):   The dependency graph of the model.
			curIt (int):                        The current iteration value.
			time (float):                       The current simulation time.
		"""
		if self.recompte_at is True:
			return self.schedule(depGraph, curIt, time)
		else:
			for it in self.recompte_at:
				if it == curIt:
					self.__last_schedule = self.schedule(depGraph, curIt, time)
					break
			if self.__last_schedule is None:  # Force computation of schedule
				self.__last_schedule = self.schedule(depGraph, curIt, time)
			return self.__last_schedule

	def schedule(self, depGraph, curIt, time):
		"""
		Obtains the actual schedule.

		Args:
			depGraph (CBD.depGraph.DepGraph):   The dependency graph of the model.
			curIt (int):                        The current iteration value.
			time (float):                       The current simulation time.
		"""
		raise NotImplementedError()  # pragma: no cover


class TopologicalScheduler(Scheduler):
	"""
	Does a topological sort of the dependency graph, using Tarjan's algorithm.

	Note:
		This code was previously located in the :class:`pyCBD.depGraph.DepGraph` and
		hence, it was written by Marc Provost.
	"""
	def schedule(self, depGraph, curIt, time):
		mapping = depGraph.getSemanticMapping()
		components = []
		sortedList = self.topoSort(mapping, depGraph)

		for object in mapping.keys():
			depGraph.unMark(object)

		sortedList.reverse()

		for object in sortedList:
			if not depGraph.isMarked(object):
				component = []
				self.dfsCollect(depGraph, object, component, curIt)
				components.append(component)

		components.reverse()
		return components

	def topoSort(self, mapping, depGraph):
		"""
		Performs a topological sort on the graph.

		Args:
			mapping (dict):                     Semantic mapping of the dependency graph
			depGraph (CBD.depGraph.DepGraph):   The dependency graph
		"""
		for object in mapping.keys():
			depGraph.unMark(object)

		sortedList = []

		for object in mapping.keys():
			if not depGraph.isMarked(object):
				self.dfsSort(depGraph, object, sortedList)

		return sortedList

	def dfsSort(self, depGraph, object, sortedList):
		"""
		Performs a depth first search, collecting the objects in
		topological order.

		Args:
			depGraph (CBD.depGraph.DepGraph):   The dependency graph
			object:                             The currently visited object
			sortedList (list):                  Partially sorted list of objects
		"""
		if not depGraph.isMarked(object):
			depGraph.mark(object)

			for influencer in depGraph.getInfluencers(object):
				self.dfsSort(depGraph, influencer, sortedList)

			sortedList.append(object)

	def dfsCollect(self, depGraph, object, component, curIt):
		"""
		Collects members of a strong component.

		Args:
			depGraph (CBD.depGraph.DepGraph):   The dependency graph
			object:                             Node currently visited
			component (list):                   Current component
			curIt (int):                        The current iteration
		"""
		if not depGraph.isMarked(object):
			depGraph.mark(object)

			for dependent in depGraph.getDependents(object):
				self.dfsCollect(depGraph, dependent, component, curIt)

			component.append(object)
