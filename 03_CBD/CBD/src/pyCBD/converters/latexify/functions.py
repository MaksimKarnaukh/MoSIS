"""
New and improved LaTeX-generation module.
"""
import copy
from copy import deepcopy


class Time:
	"""
	Represents the time variable to be used in the equations.

	Args:
		value (numeric):    The value of the time.
		relative (bool):    When :code:`True`, the time is relative to some time variable.
							When :code:`False`, the time is meant to be an absolute time.
	"""
	def __init__(self, value, relative=False):
		self.value = value
		self.relative = relative

	def __eq__(self, other):
		return other.value == self.value and other.relative == self.relative

	def __add__(self, other):
		if isinstance(other, (int, float)):
			return Time(self.value + other, self.relative)
		if self.is_relative() and other.is_relative():
			return Time(self.value + other.value, True)
		if self.is_absolute() or other.is_absolute():
			return Time(self.value + other.value)
		raise TypeError("unsupported operand type(s) for +: '%s' and 'Time'" % str(other.__class__))

	def __str__(self):
		if self.is_relative():
			if self.value == 0:
				return "{i}"
			elif self.value > 0:
				return "{i} + " + str(self.value) + "{dt}"
			elif self.value < 0:
				return "{i} - " + str(abs(self.value)) + "{dt}"
		else:
			return str(self.value)

	def is_absolute(self):
		return not self.relative

	def is_relative(self):
		return self.relative

	@staticmethod
	def now():
		return Time(0, True)


class Eq:
	"""
	Represents an equation in the form of :math:`y = f(x)` .

	Args:
		lhs (str):      The lefthandside of the equation, i.e.,
						a variable name.
		rhs (Fnc):      The righthandside of the equation, i.e.,
						a function call.
		time (Time):    A time constraint for the full equation.
	"""
	def __init__(self, lhs, rhs, time=Time.now()):
		self.lhs = lhs
		self.rhs = rhs
		self.time = time

	def __repr__(self):
		return "%s = %s" % (self.lhs, str(self.rhs))

	def at(self, time):
		"""
		Some equations have multiple solutions for a specific time.
		This function will obtain all corresponding equations for
		solving the current one at time :attr:`time`.

		Args:
			time (Time):    The current time to solve the equation at.

		Returns:
			A list of new equations, solved at a specific time.
		"""
		rhs_list = self.rhs.at(time)
		eq_list = []
		for rhs in rhs_list:
			if isinstance(rhs, ConstantFnc):
				rhs.time = rhs.eq_time
			eq_list.append(Eq(self.lhs, rhs, rhs.eq_time))
		return eq_list

	def get_dependencies(self):
		if isinstance(self.rhs, VarFnc):
			return [self.rhs]
		return self.rhs.get_dependencies()

	def eq(self):
		return "{lhs}{{E}} = {rhs}".format(lhs=self.lhs, rhs=self.rhs.eq())

	def latex(self):
		return "{lhs}{{E}} = {rhs}".format(lhs=self.lhs, rhs=self.rhs.latex())

	def apply(self, other):
		self.rhs = self.rhs.apply(other)

	def simplify(self):
		"""
		Simplifies the rhs.
		"""
		rhs = self.rhs.simplify()
		res = []
		for r in rhs:
			eq = Eq(self.lhs, r, self.time)
			res.append(eq)
		return res


class Fnc:
	"""
	Representation of a righthandside of an equation.
	This is an superclass for all specific function types.

	Args:
		name (str):     The name for the function.

	Keyword Args:
		time (Time):    The current time for this function.
		eq_time (Time): The current equation time for this function.
	"""
	def __init__(self, name, time=Time.now(), eq_time=Time.now()):
		self.name = name
		self.args = []

		# Time properties
		self.time = time
		self.eq_time = eq_time

	def __str__(self):
		return "%s(%s){%s}" % (self.name, ", ".join([str(x) for x in self.args]), str(self.time))

	def __repr__(self):
		return str(self)

	def __eq__(self, other):
		return self.name == other.name and self.time == other.time and self.eq_time == other.time and \
				self.args == other.args

	def __hash__(self):
		return hash(self.name)

	def simplify(self):
		"""
		Simplifies the function in-line, based on its arguments.
		"""
		return [self]

	def latex(self):
		"""
		Returns the LaTeX-representation of the function.
		"""
		return "%s(%s)" % (self.name, ", ".join([x.latex() for x in self.args]))

	def eq(self):
		"""
		Returns the textual equation-based representation of the function.
		"""
		return "%s(%s)" % (self.name, ", ".join([x.eq() for x in self.args]))

	def get_dependencies(self):
		"""
		Recursively obtains the dependencies of the current function.
		"""
		res = []
		for a in self.args:
			if isinstance(a, VarFnc):
				res.append(a)
			else:
				res += a.get_dependencies()
		return res

	def at(self, time):
		"""
		Computes the function at a specific point in time.

		Args:
			time (Time):    The time when to evaluate the function.

		Returns:
			A list of new functions.
		"""
		fncsets = []
		for arg in self.args:
			fncsets.append([x for x in arg.at(time)])
		if len(fncsets) == 0:
			args = []
		elif len(fncsets) == 1:
			args = [a for a in fncsets]
		else:
			args = self._cross_product_fncs(*fncsets)
		for a in args:
			k = self.create(a[0].time, a[0].eq_time)
			k.args = a
			yield k
		if len(args) == 0:
			yield self.create(time, time)

	def create(self, time, eq_time):
		return self.__class__(self.name, time, eq_time)

	def apply(self, eq):
		for i, a in enumerate(self.args):
			res = a.apply(eq)
			self.args[i] = res
		return self

	def contains(self, other):
		"""
		Checks if the function relies on another value.

		Args:
			other (str):    The name that must be checked.
		"""
		for arg in self.args:
			if arg.contains(other):
				return True
		return False

	@staticmethod
	def _cross_product_fncs(l1, l2, *lists):
		res = []
		for e1n in l1:
			for e2n in l2:
				if isinstance(e1n, list):
					e1 = deepcopy(e1n)
					e1.append(deepcopy(e2n))
				else:
					e1 = [deepcopy(e1n), deepcopy(e2n)]
				# TODO: Only do this if
				#       all elements have the same equation time
				#       (assuming the equation time is either NOW or at some absolute time)
				res.append(e1)
					# if e1.eq_time == e2.eq_time:
					# 	res.append(Fnc(self.name, e1, e2, eq_time=e1.eq_time))
					# elif e1.eq_time.is_absolute() and e2.eq_time.is_relative():
					# 	e2.eq_time += e1.eq_time
					# 	e2.time += e1.eq_time
					# 	res.append(Fnc(self.name, e1, e2, time=e1.time, eq_time=e2.eq_time))
					# elif e2.eq_time.is_absolute() and e1.eq_time.is_relative():
					# 	e1.eq_time += e2.eq_time
					# 	e1.time += e2.eq_time
					# 	res.append(Fnc(self.name, e1, e2, time=e2.time, eq_time=e2.eq_time))
					# elif e1.eq_time.is_relative() and e2.eq_time.is_relative():
					# 	eq_time = e1.eq_time + e2.eq_time
					# 	if eq_time != e1.eq_time:
					# 		e1.eq_time = eq_time
					# 		e1.time += eq_time
					# 	if eq_time != e2.eq_time:
					# 		e2.eq_time = eq_time
					# 		e2.time += eq_time
					# 	res.append(Fnc(self.name, e1, e2))
		if len(lists) > 0:
			return Fnc._cross_product_fncs(res, *lists)
		return res


class MultiFnc(Fnc):
	"""
	Collection function for both the adder and the product blocks
	"""
	def __init__(self, name, symbol, time=Time.now(), eq_time=Time.now()):
		Fnc.__init__(self, name, time=time, eq_time=eq_time)
		self.symbol = symbol

	def create(self, time, eq_time):
		return self.__class__(self.name, self.symbol, time, eq_time)

	def eq(self):
		return "(" + (" " + self.name + " ").join([a.eq() for a in self.args]) + ")"

	def latex(self):
		return "(" + (" " + self.symbol + " ").join([a.latex() for a in self.args]) + ")"

	def simplify(self):
		unary = 0.0
		if self.name == "*":
			unary = 1.0
		const = ConstantFnc("C", unary, self.time, self.eq_time)
		counts = {}
		for arg in self.args:
			if isinstance(arg, ConstantFnc) and isinstance(arg.val, (int, float)):
				if self.name == '+':
					const.val += arg.val
				elif self.name == '*':
					const.val *= arg.val
			else:
				if arg not in list(counts.keys()):
					counts[arg] = 0
				counts[arg] += 1
		if len(counts) == 0 or const.val != unary:
			if const not in list(counts.keys()):
				counts[const] = 0
			counts[const] += 1

		others = []
		for a, c in counts.items():
			if c == 1:
				others.append(a)
			else:
				if self.name == '+':
					na = BLOCK_MAP["ProductBlock"](None)[0]
				elif self.name == '*':
					na = BLOCK_MAP["PowerBlock"](None)[0]
				else:
					continue
				na.time = self.time
				na.eq_time = self.eq_time
				na.args = [a, ConstantFnc("C", c, self.time, self.eq_time)]
				others.append(na)

		if len(counts) == 1:
			return [others[0]]
		self.args = others
		return [self]


class UnaryFnc(Fnc):
	"""
	Collection function for unary input functions
	"""
	def __init__(self, name, symbol, time=Time.now(), eq_time=Time.now()):
		Fnc.__init__(self, name, time=time, eq_time=eq_time)
		self.symbol = symbol

	def create(self, time, eq_time):
		return self.__class__(self.name, self.symbol, time, eq_time)

	def eq(self):
		return "(" + self.name + self.args[0].eq() + ")"

	def latex(self):
		return "(" + self.symbol + self.args[0].latex() + ")"

	def simplify(self):
		if isinstance(self.args[0], ConstantFnc):
			if isinstance(self.args[0].val, str):
				ret = self.create(self.time, self.eq_time)
				ret.args = self.args[:]
				return [ret]
			if self.name == '-':
				self.args[0].val *= -1
				return [self.args[0]]
			elif self.name == '~':
				self.args[0].val = 1 / self.args[0].val
				return [self.args[0]]
			elif self.name == '!':
				self.args[0].val = not self.args[0].val
				return [self.args[0]]
		elif isinstance(self.args[0], UnaryFnc) and self.args[0].name == self.name:
			return [self.args[0].args[0]]
		return [self]


class BinaryFnc(Fnc):
	"""
	Collection function for binary input functions
	"""
	def __init__(self, name, symbol, time=Time.now(), eq_time=Time.now()):
		Fnc.__init__(self, name, time=time, eq_time=eq_time)
		self.symbol = symbol

	def create(self, time, eq_time):
		return self.__class__(self.name, self.symbol, time, eq_time)

	def eq(self):
		return "(" + self.name.format(a=self.args[0].eq(), b=self.args[1].eq()) + ")"

	def latex(self):
		return "(" + self.symbol.format(a=self.args[0].latex(), b=self.args[1].latex()) + ")"

	def simplify(self):
		if self.name in ["{a}^(1/{b})", "{a}^{b}"]:
			if isinstance(self.args[1], ConstantFnc) and self.args[1].val == 1:
				return [self.args[0]]
			elif isinstance(self.args[0], ConstantFnc) and self.args[0].val == 1:
				return [self.args[0]]
			elif isinstance(self.args[0], ConstantFnc) and isinstance(self.args[1], ConstantFnc):
				self.args[0].val = eval(self.eq())
				return [self.args[0]]
		return [self]


class ConstantFnc(Fnc):
	"""
	Function that represents a constant value
	"""
	def __init__(self, name, val, time=Time.now(), eq_time=Time.now()):
		Fnc.__init__(self, name, time=time, eq_time=eq_time)
		self.val = val

	def create(self, time, eq_time):
		return self.__class__(self.name, self.val, time, eq_time)

	def __str__(self):
		return str(self.val)

	def __eq__(self, other):
		return Fnc.__eq__(self, other) and self.val == other.val

	def __hash__(self):
		return hash(self.name)

	def eq(self):
		return str(self.val)

	def latex(self):
		return str(self.val)

	def at(self, time):
		self.eq_time = time
		return [self]


class VarFnc(Fnc):
	"""
	Function that represents a variable name
	"""
	def __init__(self, name, time=Time.now(), eq_time=Time.now()):
		Fnc.__init__(self, name, time=time, eq_time=eq_time)

	def __str__(self):
		return str(self.name)

	def eq(self):
		return "%s{T}" % str(self.name)

	def latex(self):
		return "%s{T}" % str(self.name)

	def at(self, time):
		self.time = time
		self.eq_time = time
		return [self]

	def apply(self, eq):
		if self.name == eq.lhs:
			return eq.rhs
		return self

	def contains(self, other):
		return self.name == other


class DelayFnc(Fnc):
	def at(self, time):
		res = []
		res += self.args[1].at(Time(0))
		if time != Time(0):
			res += self.args[0].at(time + Time(-1, True))
			res[-1].eq_time = time
		return res


class DerivatorFnc(Fnc):
	"""
		Function that represents a derivative
	"""
	def __init__(self, name, time=Time.now(), eq_time=Time.now()):
		Fnc.__init__(self, name, time=time, eq_time=eq_time)

	def eq(self):
		return "der(%s, 0, {T})" % self.args[0].eq()

	def latex(self):
		return "\\frac{\\partial}{\\partial {dt}} (%s)" % self.args[0].latex()

	def at(self, time):
		if time == Time(0):
			return self.args[1].at(time)
		return Fnc.at(self, time)


class IntegratorFnc(Fnc):
	"""
		Function that represents an integral
	"""
	def __init__(self, name, time=Time.now(), eq_time=Time.now()):
		Fnc.__init__(self, name, time=time, eq_time=eq_time)

	def eq(self):
		return "integ(%s, 0, {T})" % self.args[0].eq()

	def latex(self):
		return "\\int_0^{{T}} (%s) d{dt}" % self.args[0].latex()

	def at(self, time):
		if time == Time(0):
			return self.args[1].at(time)
		return Fnc.at(self, time)


BLOCK_MAP = {
	"ConstantBlock": lambda block: [ConstantFnc("C", block.getValue())],
	"NegatorBlock": lambda block: [UnaryFnc("-", "-")],
	"InverterBlock": lambda block: [UnaryFnc("~", "1 / ")],
	"AdderBlock": lambda block: [MultiFnc("+", "+")],
	"ProductBlock": lambda block: [MultiFnc("*", "\\cdot")],
	"ModuloBlock": lambda block: [BinaryFnc("{a} mod {b}", "{a} % {b}")],
	"RootBlock": lambda block: [BinaryFnc("{a}^(1/{b})", "{a}^(1/{b})")],
	"PowerBlock": lambda block: [BinaryFnc("{a}^{b}", "{a}^{b}")],
	"GenericBlock": lambda block: [Fnc(block.getBlockOperator())],
	"LessThanBlock": lambda block: [BinaryFnc("<", "{a} < {b}")],
	"LessThanOrEqualsBlock": lambda block: [BinaryFnc("<=", "{a} \\lte {b}")],
	"EqualsBlock": lambda block: [BinaryFnc("==", "{a} \\leftrightarrow {b}")],
	"NotBlock": lambda block: [UnaryFnc("!", "\\neg")],
	"OrBlock": lambda block: [BinaryFnc("or", "{a} \\wedge {b}")],
	"AndBlock": lambda block: [BinaryFnc("and", "{a} \\vee {b}")],
	"TimeBlock": lambda block: [VarFnc("time")],
	"DeltaTBlock": lambda block: [ConstantFnc("C", "{dt}")],
	"DelayBlock": lambda block: [DelayFnc("D")],
	"DerivatorBlock": lambda block: [DerivatorFnc("Der")],
	"IntegratorBlock": lambda block: [IntegratorFnc("Int")],
}
"""
The mapping for all known blocks in CBDs. If you created your own block with its own representation,
you need to set it in the :code:`type_formats` of the :class:`pyCBD.converters.latexify.CBD2Latex` class.
"""


if __name__ == '__main__':
	l1 = [Fnc('+'), Fnc('IC1', time=Time(0), eq_time=Time(0))]
	l2 = [Fnc('IC2')]
	l3 = [Fnc('q', time=Time(-1, True)), Fnc('IC3', time=Time(0), eq_time=Time(0))]

	fnc = Fnc('+')
	fncs = fnc._cross_product_fncs(l1, l2)
	print(fncs)
