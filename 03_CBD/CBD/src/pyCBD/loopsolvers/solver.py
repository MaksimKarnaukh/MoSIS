"""
Algebraic loops can be complex to solve.
This module provides a base class for all loop solvers.
"""

import logging

class Solver:
	"""
	Superclass that can solve algebraic loops.

	Args:
		logger (Logger):    The logger to use.
	"""
	def __init__(self, logger=None):
		if logger is None:
			logger = logging.getLogger("CBD")
		self._logger = logger

	def checkValidity(self, path, component):
		"""
		Checks the validity of an algebraic loop.

		Args:
			path (str):         The path of the top-level block.
			component (list):   The blocks in the algebraic loop.
		"""
		raise NotImplementedError()

	def constructInput(self, component, curIt):
		"""
		Constructs input for the solver.

		Args:
			component (list):   The blocks in the algebraic loop.
			curIt (int):        The current iteration of the simulation.

		See Also:
			:func:`solve`
		"""
		raise NotImplementedError()

	def solve(self, solverInput):
		"""
		Solves the algebraic loop.

		Args:
			solverInput:    The constructed input.

		See Also:
			:func:`constructInput`
		"""
		raise NotImplementedError()
