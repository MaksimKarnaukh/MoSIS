"""Set of extra library blocks for more CBD possibilities.

These blocks will only be available if the corresponding packages are installed.
"""
from pyCBD.Core import BaseBlock

try:
	from fuzzylogic.classes import Domain, Rule

	class FuzzyBlock(BaseBlock):
		"""
		CBD block that integrates with the fuzzylogic library to allow
		for more extensive functionalities.

		Arguments:
			block_name (str):   The name of the block.
			domains (iter):     An iterable that contains all the Domains.
			rules (Rule):       All the Rules for the fuzzy logic.

		:Input Ports:
			For each domain, an input port is added with the domain name as name. It takes a
			crisp input value from the external CBD model.

		:Output Ports:
			**OUT1** -- A crisp output value that corresponds to the fuzzy value(s).
		"""
		def __init__(self, block_name, domains, rules):
			super().__init__(block_name, [], ["OUT1"])
			self.rules = rules

			self.domains = dict()
			for dom in domains:
				self.domains[dom._name] = dom
				self.addInputPort(dom._name)

		def compute(self, curIteration):
			vals = dict()
			for inp in self.getInputPortNames():
				vals[self.domains[inp]] = self.getInputSignal(curIteration, inp)
			self.appendToSignal(self.rules(vals), "OUT1")

except ImportError: pass
