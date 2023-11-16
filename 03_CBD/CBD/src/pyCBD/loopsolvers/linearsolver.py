"""
This module provides a Gauss-Jordan solver to solve linear algebraic loops.
"""

import math

from pyCBD.util import PYTHON_VERSION
from pyCBD.loopsolvers.solver import Solver


class _StrVar:
	def __init__(self, val):
		self.vals = val

	def __add__(self, other):
		self.vals += ' + ' + str(other)
		return self

	def __mul__(self, other):
		self.vals += ' * ' + str(other)
		return self

	def __str__(self):
		return self.vals

	def __repr__(self):
		return str(self)


class LinearSolver(Solver):
	"""
	Solves linear algebraic loops using matrices.
	"""
	def checkValidity(self, path, component):
		if not self.__isLinear(component):
			self._logger.critical("Cannot solve non-linear algebraic loop.\nSelf: {}\nComponents: {}".format(path, component), extra={"blockname": "Algebraic Loop"})

	def __isLinear(self, strongComponent):
		"""Determines if an algebraic loop describes a linear equation or not.

		For a block to comprise the strong component, at least one of its dependencies must be in the strong
		component as well.

		Args:
			strongComponent (list): The detected loop, in a list (of BaseBlock instances)

		Returns:
			:class:`True` if the loop is linear, else :code:`False`.
		"""
		# TO IMPLEMENT

		"""
		A non-linear equation is generated when the following conditions occur:
		 (1) there is a multiplication operation being performed between two unknowns.
		 (2) there is an invertion operation being performed in an unknown.
		 (3) some non-linear block belongs to the strong component
	
		The condition (1) can be operationalized by finding a product block that has two dependencies belonging to
		the strong component. This will immediatly tell us that it is a product between two unknowns.
		The condition (2) can be operationalized simply by finding an inverter block in the strong component. 
		Because the inverter block only has one input, if it is in the strong component, it means that its only
		dependency is in the strong component.
		"""

		# WON'T APPEAR: Constant, Sequence, Time, Logging
		# LINEAR: Negator, Adder, Delay, Input, Output, Wire
		# NON-LINEAR: Inverter, Modulo, Root, LT, EQ, LTE, Not, Or, And, MUX, Generic, ABS, Int, Power, Min, Max, Clamp
		# SEMI-LINEAR: Product // MUX?

		for block in strongComponent:
			# condition (1)
			if block.getBlockType() == "ProductBlock":
				dependenciesUnknown = [x for x in block.getDependencies(0) if x.block in strongComponent]
				if len(dependenciesUnknown) >= 2:
					return False

			# condition (2) and (3)
			if block.getBlockType() in ["InverterBlock", "ModuloBlock", "RootBlock", "LessThanBlock", "EqualsBlock",
										"LessThanOrEqualsBlock", "NotBlock", "OrBlock", "AndBlock", "MinBlock",
										"MaxBlock", "MultiplexerBlock", "GenericBlock", "AbsBlock", "IntBlock",
										"PowerBlock", "ClampBlock"]:
				return False

		return True

	def constructInput(self, strongComponent, curIteration):
		"""
		Constructs input for a solver of systems of linear equations
		Input consists of two matrices:

			- M1: coefficient matrix, where each row represents an equation of the system
			- M2: result matrix, where each element is the result for the corresponding equation in M1
		"""
		sep = '.'
		known = {}
		for block in strongComponent:
			for inp in block.getInputPorts():
				fblock = inp.getPreviousPortClosure().block
				# fblock = block.getPortConnectedToInput(inp.name).block
				if fblock not in strongComponent:
					val = inp.getHistory()[curIteration].value
					known[block.getPath(sep) + sep + inp.name] = val
					known[fblock.getPath(sep)] = val
		try:
			return self.get_matrix(strongComponent, sep, known)
		except ValueError as e:
			self._logger.exception(str(e), extra={"block": "Strong Component"})

	@staticmethod
	def get_matrix(strongComponent, sep='.', known=None):
		if known is None:
			known = {}

		# Initialize matrices with zeros
		size = len(strongComponent)
		M1 = Matrix(size, size)
		M2 = [0] * size

		# block -> index of block
		indexdict = dict()

		for i, block in enumerate(strongComponent):
			indexdict[block] = i

		# Get list of low-level dependencies from n inputs
		def getBlockDependencies2(block):
			return (port.block for port in [x.getPreviousPortClosure() for x in block.getInputPorts()])

		for i, block in enumerate(strongComponent):
			if block.getBlockType() == "AdderBlock":
				for external in [x for x in getBlockDependencies2(block) if x not in strongComponent]:
					if external.getPath(sep) in known:
						M2[i] -= known[external.getPath(sep)]
					else:
						for inp in block.getInputPortNames():
							if block.getPortConnectedToInput(inp).block == external:
								path = block.getPath(sep) + sep + inp
								M2[i] = _StrVar(str(M2[i]) + " - " + known.get(path, path))
								break
				M1[i, i] = -1

				for compInStrong in [x for x in getBlockDependencies2(block) if x in strongComponent]:
					M1[i, indexdict[compInStrong]] += 1
			elif block.getBlockType() == "ProductBlock":
				# M2 can stay 0
				M1[i, i] = -1
				fact = 1
				for external in [x for x in getBlockDependencies2(block) if x not in strongComponent]:
					if external.getPath(sep) in known:
						fact *= known[external.getPath(sep)]
					else:
						for inp in block.getInputPortNames():
							if block.getPortConnectedToInput(inp).block == external:
								path = block.getPath(sep) + sep + inp
								fact = _StrVar(str(fact) + " * " + known.get(path, path))
								break
				for compInStrong in [x for x in getBlockDependencies2(block) if x in strongComponent]:
					M1[i, indexdict[compInStrong]] = fact + M1[i, indexdict[compInStrong]]
			elif block.getBlockType() == "NegatorBlock":
				# M2 can stay 0
				M1[i, i] = -1
				possibleDep = block.getInputPortByName("IN1").getPreviousPortClosure()
				M1[i, indexdict[possibleDep.block]] = - 1
			elif block.getBlockType() == "DelayBlock":
				# If a delay is in a strong component, this is the first iteration
				# And so the dependency is the IC
				# M2 can stay 0 because we have an equation of the type -x = -ic <=> -x + ic = 0
				M1[i, i] = -1
				possibleDep = block.getPortConnectedToInput("IC")
				dependency = possibleDep.block
				assert dependency in strongComponent
				M1[i, indexdict[dependency]] = 1
			else:
				raise ValueError("Unknown element '{}', please implement".format(block.getBlockType()))
		return M1, M2

	def solve(self, solverInput):
		M1, M2 = solverInput
		n = M1.rows
		indxc = [0] * n
		indxr = [0] * n
		ipiv = [0] * n
		icol = 0
		irow = 0
		for i in range(n):
			big = 0.0
			for j in range(n):
				if ipiv[j] != 1:
					for k in range(n):
						if ipiv[k] == 0:
							nb = math.fabs(M1[j, k])
							if nb >= big:
								big = nb
								irow = j
								icol = k
						elif ipiv[k] > 1:
							raise ValueError("GAUSSJ: Singular Matrix-1")
			ipiv[icol] += 1
			if irow != icol:
				for l in range(n):
					M1[irow, l], M1[icol, l] = M1[icol, l], M1[irow, l]
				M2[irow], M2[icol] = M2[icol], M2[irow]
			indxr[i] = irow
			indxc[i] = icol
			if M1[icol, icol] == 0.0:
				raise ValueError("GAUSSJ: Singular Matrix-2")
			pivinv = 1.0 / M1[icol, icol]
			M1[icol, icol] = 1.0
			for l in range(n):
				M1[icol, l] *= pivinv
			M2[icol] *= pivinv
			for ll in range(n):
				if ll != icol:
					dum = M1[ll, icol]
					M1[ll, icol] = 0.0
					for l in range(n):
						M1[ll, l] -= M1[icol, l] * dum
					M2[ll] -= M2[icol] * dum

		for l in range(n - 1, 0, -1):
			if indxr[l] != indxc[l]:
				for k in range(n):
					M1[k, indxr[l]], M1[k, indxc[l]] = M1[k, indxc[l]], M1[k, indxr[l]]

		return solverInput[1]


class Matrix:
	"""Custom, efficient matrix class. This class is used for efficiency purposes.

		- Using a while/for loop is slow.
		- Using :class:`[[0] * n] * n` will have n references to the same list.
		- Using :class:`[[0] * size for _ in range(size)]` can be 5 times slower
		  than this class!

	Numpy could be used to even further increase efficiency, but this increases the
	required dependencies for external hardware systems (that may not provide these options).

	Note:
		Internally, the matrix is segmented into chunks of 500.000.000 items.
	"""
	def __init__(self, rows, cols):
		self.rows = rows
		self.cols = cols
		self.size = rows * cols
		self.__max_list_size = 500 * 1000 * 1000
		self.data = [[0] * ((rows * cols) % self.__max_list_size)]
		for r in range(self.size // self.__max_list_size):
			self.data.append([0] * self.__max_list_size)

	def __getitem__(self, idx):
		absolute = idx[0] * self.cols + idx[1]
		outer = absolute // self.__max_list_size
		inner = absolute % self.__max_list_size
		return self.data[outer][inner]

	def __setitem__(self, idx, value):
		absolute = idx[0] * self.cols + idx[1]
		outer = absolute // self.__max_list_size
		inner = absolute % self.__max_list_size
		self.data[outer][inner] = value

	def __str__(self):
		return self.format()

	def format(self, sep='\t', paren='[]', floats="%8.4f", eol='\n'):
		res = ""
		for row in range(self.rows):
			if len(res) > 0:
				res += eol
			res += paren[0]
			for col in range(self.cols):
				if isinstance(self[row, col], _StrVar):
					res += sep + str(self[row, col])
				else:
					res += sep + floats % self[row, col]
			res += sep + paren[1]
		return res

	def concat(self, other):
		if isinstance(other, list):
			om = Matrix(len(other), 1)
			for i, e in enumerate(other):
				om[i, 0] = e
			return self.concat(om)
		assert other.rows == self.rows
		res = Matrix(self.rows, self.cols + other.cols)
		for r in range(self.rows):
			for c in range(self.cols):
				res[r, c] = self[r, c]
			for c in range(other.cols):
				res[r, c + self.cols] = other[r, c]
		return res
