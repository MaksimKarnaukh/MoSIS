"""
This module implements a dependency graph

:Original Author:        Marc Provost
"""
from .Core import CBD, BaseBlock, Port
import copy


class DepNode:
	"""Class implementing a node in the dependency graph.

	Args:
		object: Reference to a semantic object identifying the node
	"""

	def __init__(self, object):
		self.__object = object
		self.__isMarked = False

	def mark(self):
		"""
		Marks the node.
		"""
		self.__isMarked = True

	def unMark(self):
		"""
		Unmarks the node.
		"""
		self.__isMarked = False

	def isMarked(self):
		"""
		Checks if the node is marked.
		"""
		return self.__isMarked

	def getMappedObj(self):
		"""
		Gets the object that this node refers to.
		"""
		return self.__object

	def __repr__(self):
		return "DepNode :: " + str(self.__object)


class DepGraph:
	"""
	Class implementing dependency graph.
	"""
	def __init__(self, ignore_hierarchy=False):
		self.ignore_hierarchy = ignore_hierarchy

		# Dict holding a mapping "Object -> DepNode"
		self.__semanticMapping = {}

		# map object->list of objects depending on object
		self.__dependents = {}
		# map object->list of objects that influences object
		self.__influencers = {}

	def __repr__(self):
		repr = "Dependents: \n"
		for dep in self.__dependents:
			if isinstance(dep, Port):
				name = dep.name
			else:
				name = dep.getBlockName()
			repr += name + ":" + str(self.__dependents[dep]) + "\n"
		repr += "Influencers: \n"
		for infl in self.__influencers:
			if isinstance(infl, Port):
				name = infl.name
			else:
				name = infl.getBlockName()
			repr += name + ":" + str(self.__influencers[infl]) + "\n"
		return repr

	def addMember(self, object):
		"""Add an object mapped to this graph.

		Args:
			object:     the object to be added

		Raises:
			ValueError: If object is already in the graph
		"""
		if not self.hasMember(object):
			if not isinstance(object, CBD) or self.ignore_hierarchy:
				node = DepNode(object)
				self.__dependents[object] = []
				self.__influencers[object] = []
				self.__semanticMapping[object] = node
			else:
				for block in object.getBlocks():
					self.addMember(block)
			# if isinstance(object, BaseBlock):
			# 	for port in object.getInputPorts() + object.getOutputPorts():
			# 		self.addMember(port)
		else:
			raise ValueError("Specified object is already member of this graph")

	def hasMember(self, object):
		"""
		Checks if the object is already mapped.

		Args:
			object: The object to be checked.
		"""
		return object in self.__semanticMapping

	def removeMember(self, object):
		""" Remove a object from this graph.

		Args:
			object:     the object to be removed

		Raises:
			ValueError: If object is not in the graph
		"""
		if self.hasMember(object):
			for dependent in self.getDependents(object):
				self.__influencers[dependent].remove(object)
			for influencer in self.getInfluencers(object):
				self.__dependents[influencer].remove(object)

			del self.__dependents[object]
			del self.__influencers[object]
			del self.__semanticMapping[object]
		else:
			raise ValueError("Specified object is not member of this graph")

	def setDependency(self, dependent, influencer, curIt):
		"""Creates a dependency between two objects.

		Args:
		   dependent:   The object which depends on the :attr:`influencer`.
		   influencer:  The object which influences the :attr:`dependent`.

		Raises:
			ValueError: if depedent or influencer is not member of this graph
			ValueError: if the dependency already exists
		"""
		# TODO: fix infinite cycle when passing straight through
		# TODO: fix errors when multi-level connection

		# Link CBD outputs
		if isinstance(influencer, CBD) and not self.ignore_hierarchy:
			# When there is more than one connection from a CBD to one and the same block,
			# more than one dependency should be set, as there is more than one underlying
			# connection
			for inp in dependent.getInputPorts():
				inf_out = inp.getIncoming().source
				if inf_out.block == influencer:
					inf = inp.getPreviousPortClosure()
					self.setDependency(dependent, inf.block, curIt)
			return

		# Link CBD inputs
		if isinstance(dependent, CBD) and not self.ignore_hierarchy:
			# When there is more than one connection from a CBD to one and the same block,
			# more than one dependency should be set, as there is more than one underlying
			# connection
			for inp in dependent.getInputPorts():
				inf_out = inp.getPreviousPortClosure()
				if inf_out.block == influencer:
					for dep in inp.getNextPortClosure():
						# When direction == OUT; the port is simply unused!
						if dep.direction == Port.Direction.IN:
							self.setDependency(dep.block, influencer, curIt)
			return

		if self.hasMember(dependent) and self.hasMember(influencer):
			if not influencer in self.__influencers[dependent] and \
					not dependent in self.__dependents[influencer]:
				self.__influencers[dependent].append(influencer)
				self.__dependents[influencer].append(dependent)
		else:
			if not self.hasMember(dependent):
				raise ValueError("Specified dependent object is not member of this graph")
			if not self.hasMember(influencer):
				raise ValueError("Specified influencer object is not member of this graph")

	def hasDependency(self, dependent, influencer):
		"""
		Checks if the influencer influences the dependent and if the dependent is dependent
		on the influencer.

		Args:
			dependent:  The object which depends on the other
			influencer: The object which influences the other
		"""
		assert self.hasMember(dependent), "Specified dependent object is not member of this graph"
		assert self.hasMember(influencer), "Specified influencer object is not member of this graph"
		return influencer in self.__influencers[dependent] and \
		       dependent in self.__dependents[influencer]

	def unsetDependency(self, dependent, influencer):
		""" Removes a dependency between two objects.

		Args:
			dependent:  The object which depends on the other
			influencer: The object which influences the other

		Raises:
			ValueError: if depedent or influencer is not member of this graph
			ValueError: if the dependency does not exists
		"""
		if self.hasMember(dependent) and self.hasMember(influencer):
			if influencer in self.__influencers[dependent] and \
					dependent in self.__dependents[influencer]:
				self.__influencers[dependent].remove(influencer)
				self.__dependents[influencer].remove(dependent)
			else:
				raise ValueError("Specified dependency does not exists")
		else:
			if not self.hasMember(dependent):
				raise ValueError("Specified dependent object is not member of this graph")
			if not self.hasMember(influencer):
				raise ValueError("Specified influencer object is not member of this graph")

	def getDependents(self, object):
		"""
		Obtains all dependents of a specific object.

		Args:
			object: The object to get the dependents from.
		"""
		if self.hasMember(object):
			return copy.copy(self.__dependents[object])
		else:
			raise ValueError("Specified object is not member of this graph")

	def getInfluencers(self, object):
		"""
		Obtains all influencers of a specific object.

		Args:
			object: The object to get the influencers from.
		"""
		if self.hasMember(object):
			return copy.copy(self.__influencers[object])
		else:
			raise ValueError("Specified object is not member of this graph")

	def getSemanticMapping(self):
		"""
		Obtains the semantic mapping of the graph.

		Returns:
			A dictionary of object -> :class:`DepNode`.
		"""
		return self.__semanticMapping

	def __getDepNode(self, object):
		"""
		Gets the :class:`DepNode` of a specific object if it is
		in the semantic mapping.

		Args:
			object:     The object to get the node of.
		"""
		if self.hasMember(object):
			return self.__semanticMapping[object]
		else:
			raise ValueError("Specified object is not a member of this graph")

	def mark(self, object):
		"""
		Marks an object in the graph.

		Args:
			object: The object to mark
		"""
		self.__getDepNode(object).mark()

	def unMark(self, object):
		"""
		Unmarks an object in the graph.

		Args:
			object: The object to unmark
		"""
		self.__getDepNode(object).unMark()

	def isMarked(self, object):
		"""
		Checks if an object is marked in the graph.

		Args:
			object: The object to check
		"""
		return self.__getDepNode(object).isMarked()


def createDepGraph(model, curIteration, ignore_hierarchy=False):
	"""
	Create a dependency graph of the CBD model.
	Use the curIteration to differentiate between the first and other iterations
	Watch out for dependencies with sub-models.

	Args:
		model:              The model for which the dependency graph must be computed.
		curIteration:       The current iteration for the dependency graph.
		ignore_hierarchy:   Assume the CBD model is flat and don't call this recursively.
	"""
	blocks = model.getBlocks()
	depGraph = DepGraph(ignore_hierarchy)

	for block in blocks:
		depGraph.addMember(block)
	for port in model.getInputPorts() + model.getOutputPorts():
		depGraph.addMember(port)

	def recSetInternalDependencies(blocks, curIteration):
		"""
		Recursive call for setting the internal dependencies of the graph.

		Args:
			blocks (iter):      The list of blocks to set as dependency
			curIteration (int): The current iteration number
		"""
		for block in blocks:
			for dep in block.getDependencies(curIteration):
				if dep.block == model:
					depGraph.setDependency(block, dep, curIteration)
				else:
					depGraph.setDependency(block, dep.block, curIteration)
			if isinstance(block, CBD) and not ignore_hierarchy:
				recSetInternalDependencies(block.getBlocks(), curIteration)

	recSetInternalDependencies(blocks + model.getOutputPorts(), curIteration)

	return depGraph


def gvDepGraph(model, curIt, ignore_hierarchy=False):
	"""
	Create a Graphviz string that corresponds to the dependency graph
	at the given iteration cycle.

	Args:
		model (CBD):    The :class:`CBD` model to construct the graph for.
		curIt (int):    The iteration for which the dependency graph will
						be constructed.
	"""
	m2 = model.clone()
	if not ignore_hierarchy:
		m2.flatten()
	depGraph = createDepGraph(m2, curIt, ignore_hierarchy)
	nodes = []
	edges = []
	for block in m2.getBlocks():
		bname = block.getBlockName()
		nodes.append('{namee} [label="{type}({name})"];'.format(name=bname, namee=bname.replace(".", "_"), type=block.getBlockType()))
		for inf in depGraph.getInfluencers(block):
			if isinstance(inf, BaseBlock):
				edges.append("{} -> {};".format(block.getBlockName().replace(".", "_"), inf.getBlockName().replace(".", "_")))
			else:
				edges.append("{} -> {};".format(block.getBlockName().replace(".", "_"), inf.name.replace(".", "_")))
	return "digraph {  // time = " + str(curIt) + "\n\t" + "\n\t".join(nodes + edges) + "\n}"
