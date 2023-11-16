"""
This module provides a Sympy solver to solve the algebraic loops efficiently.
It should be able to handle non-linear equations as well.

Warning:
	This module requires :code:`sympy` to be installed.
"""

import sympy

from pyCBD.Core import CBD
from pyCBD.loopsolvers.solver import Solver


def reduce(fnc, lst):
	if len(lst) == 1:
		return lst[0]
	res = fnc(lst[0], lst[1])
	for elm in lst[2:]:
		res = fnc(res, elm)
	return res


class SympySolver(Solver):
	def __init__(self, logger=None):
		Solver.__init__(self, logger)
		self.__cache = {}

	def checkValidity(self, path, component):
		if tuple(component) not in self.__cache:
			eqs = []
			for i, block in enumerate(component):
				args = []
				for x, port in self.__dependencies(block):
					if x not in component:
						args.append(sympy.symbols(x.getPath('_') + '_' + port))
					else:
						args.append(sympy.symbols(x.getPath('_') + '_' + port))

				eqs.append((block.getPath('_') + '_OUT1', self.__OPERATIONS[block.getBlockType()](args, block)))

			sol = []
			rqs = []
			for k, v in eqs:
				x = sympy.symbols(k)
				sol.append(x)
				rqs.append(v - x)
			solution = sympy.nonlinsolve(rqs, sol)

			self.__cache[tuple(component)] = solution, sol

			if len(solution.args) > 1:
				raise RuntimeError("There are multiple solutions for this system. Please add constraints.")

		return True

	def getComponentCache(self, component):
		return self.__cache[tuple(component)]

	def constructInput(self, component, curIt):
		vrs = {}
		for block in component:
			for x, port in self.__dependencies(block):
				if x not in component:
					vrs[x.getPath('_') + '_' + port] = x.getSignalHistory()[curIt].value
		res = self.__cache[tuple(component)]
		return res, vrs

	def solve(self, solverInput):
		(solution, symbols), variables = solverInput
		return solution.args[0].subs(variables)


	# TODO: Clamp, MUX, Split, LTE, Eq, LT, not, and, or, delay
	__OPERATIONS = {
		"AdderBlock": lambda l, _: sum(l),
		"ProductBlock": lambda l, _: reduce((lambda a, b: a * b), l),
		"NegatorBlock": lambda l, _: -l[0],
		"InverterBlock": lambda l, _: 1.0/l[0],
		"ModuloBlock": lambda l, _: l[0] % l[1],
		"RootBlock": lambda l, _: sympy.root(l[0], l[1]),
		"PowerBlock": lambda l, _: l[0] ** l[1],
		"AbsBlock": lambda l, _: abs(l[0]),
		"IntBlock": lambda l, _: sympy.floor(l[0]),
		"GenericBlock": lambda l, b: getattr(sympy, b.getBlockOperator())(l[0]),
		"MaxBlock": lambda l: sympy.Max(*l),
		"MinBlock": lambda l: sympy.Min(*l),
	}

	@staticmethod
	def __dependencies(block):
		blocks = []
		for s in block.getInputPortNames():
			b, op = block.getPortConnectedToInput(s)
			while isinstance(b, CBD):
				b, op = b.getBlockByName(op).getPortConnectedToInput("IN1")
			blocks.append((b, op))
		return blocks

