"""
Transforms equations/textual denotations to CBD models.
"""
import os
from lark import Lark, Transformer, Token, ParseError

__all__ = ['eq2CBD']

class eq2CBD:
	"""
	Converts equations (textual denotation) into corresponding CBD models.

	After instantiating this class, the :func:`parse` method may be called to
	obtain the CBD model(s).

	All equations must be in the form of :code:`<output> = <expression>`, where
	:code:`<output>` identifies the name of an output of the resulting CBD and
	:code:`<expression>` defines the corresponding logic. To prevent the creation
	of an output, :code:`:=` may be used instead of :code:`=`. Multiple equations
	can be listed, separated by newlines. Variables used in the expressions will
	be linked to one another if needs be. When a variable is used without any
	descriptive reference, it will be used as an input. For instance, the text
	:code:`y = 6 * x` will be transformed into a CBD with a single output :code:`y`
	and a single input :code:`x`.

	Variable names must match the regex :code:`[a-zA-Z_][a-zA-Z0-9_]*` and must not
	be any allowed function name (see below). The variable :code:`time` is reserved
	and will be replaced by a :code:`TimeBlock`.

	The following operations are allowed and transformed w.r.t. the standard library's
	building blocks (:mod:`pyCBD.lib.std`). The order of operations applied is: parentheses,
	function calls, exponents, multiplication/division and addition/subtraction.

	- :code:`(A)`: Places sub-equation :code:`A` in parentheses, giving precedence on
	  the computation of that equation.
	- :code:`-A`: Negation of a variable or value. In the case of a constant value, no
	  additional negator will be added to the CBD, **unless** explicitly requested by
	  placing the value within parentheses: i.e. :code:`-(4)`.
	- :code:`1/A`: Inversion of a variable or value. In the case of a constant value, no
	  additional inverter will be added to the CBD, **unless** explicitly requested by
	  placing the value within parentheses: i.e. :code:`1/(4)`.
	- :code:`~A` or :code:`!A` or :code:`not A`: Adds a :code:`NotBlock` before sub-equation
	  :code:`A`.
	- :code:`A + B + C - D`: Sum of two (or more) sub-equations. Whenever a subtraction
	  is encountered, it will be replaced by an addition of the negator and the other
	  terms. In the case of a constant value, the same logic as mentioned above is applied.
	- :code:`A * B * C / D`: Multiplication of two (or more) sub-equations. Whenever a
	  division is encountered, it will be replaced by the multiplication of the inverted
	  value and other factors. In the case of a constant value, the same logic as mentioned
	  above is applied.
	- :code:`A^B`: Raises sub-equation :code:`A` to the power of sub-equation :code:`B`.
	- :code:`A % B` or :code:`A mod B`: Modulo-divides sub-equation :code:`A` by sub-equation
	  :code:`B`.
	- :code:`A == B`: Tests equality between sub-equations :code:`A` and :code:`B`.
	- :code:`A <= B`: Tests inequality between sub-equations :code:`A` and :code:`B`. The
	  :code:`LessThanOrEqualsBlock` will be used here.
	- :code:`A < B`: Tests inequality between sub-equations :code:`A` and :code:`B`. The
	  :code:`LessThanBlock` will be used here.
	- :code:`A >= B`: Tests inequality between sub-equations :code:`A` and :code:`B`. Behind
	  the scenes, this code will be handled as if it were :code:`B <= A`.
	- :code:`A > B`: Tests inequality between sub-equations :code:`A` and :code:`B`. Behind
	  the scenes, this code will be handled as if it were :code:`B < A`.
	- :code:`A or B` or :code:`A || B`: Merges both :code:`A` and :code:`B` in an
	  :code:`OrBlock`.
	- :code:`A and B` or :code:`A && B`: Merges both :code:`A` and :code:`B` in an
	  :code:`AndBlock`.
	- :code:`f(A)`: executes function :code:`f` on sub-equation :code:`A`. Besides all
	  single-argument functions from the :mod:`math` module (see the :class:`pyCBD.lib.std.GenericBlock`),
	  the allowed functions (case-insensitive) are:

	.. list-table::
	   :widths: 30 30 40
	   :header-rows: 1

	   * - function
	     - argument/input port count
	     - CBD block
	   * - :code:`int`
	     - 1
	     - :class:`pyCBD.lib.std.IntBlock`
	   * - :code:`abs`
	     - 1
	     - :class:`pyCBD.lib.std.AbsBlock`
	   * - :code:`root`
	     - 2
	     - :class:`pyCBD.lib.std.RootBlock`
	   * - :code:`sqrt`
	     - 1
	     - :class:`pyCBD.lib.std.RootBlock` with second input fixed to 2
	   * - :code:`clamp` or :code:`sat`
	     - 3
	     - :class:`pyCBD.lib.std.ClampBlock`
	   * - :code:`mux`
	     - 3 (last argument is the :code:`select` input)
	     - :class:`pyCBD.lib.std.MultiplexerBlock`
	   * - :code:`d`
	     - 2 (second argument is the :code:`IC`)
	     - :class:`pyCBD.lib.std.DelayBlock`
	   * - :code:`der`
	     - 3 (second argument is the :code:`IC`, third is the :code:`delta_t`)
	     - :class:`pyCBD.lib.std.DerivatorBlock`
	   * - :code:`i`
	     - 3 (second argument is the :code:`IC`, third is the :code:`delta_t`)
	     - :class:`pyCBD.lib.std.IntegratorBlock`
	"""
	def __init__(self):
		filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "eq.lark")
		with open(filename) as file:
			contents = file.read()
		self.parser = Lark(contents, parser="earley")

	def parse(self, text, model=None):
		"""
		Parses the text and constructs a CBD model thereof.

		Args:
			text (str): The text to parse.
			model:      An optional CBD model to use for the construction.
		"""
		tree = self.parser.parse(text)
		transformer = EqTransformer(model)
		return transformer.transform(tree)


from pyCBD.Core import CBD
from pyCBD.lib.std import *
import math

class EqFunctions:
	"""
	Collection class for all the functions that can be called in the
	textual mode. They are given as member functions of this class.
	Each of these functions should return a tuple of
	:code:`block, n[, mapping]`, where :code:`block` indicates the block
	to link in the transformer, :code:`n` identifies the amount of arguments
	and the optional :code:`mapping` is a dictionary used when the ports are
	not named w.r.t. :code:`IN\\d+`.

	Args:
		model:  The model to add the blocks to.
	"""
	def __init__(self, model):
		self.model = model

	def _has_func(self, fname):
		"""
		Checks if a function exists.
		"""
		return fname in [x for x in dir(self) if callable(getattr(self, x)) and not x.startswith("_")]

	def int(self):
		block = IntBlock("")
		self.model.addBlock(block)
		return block, 1

	def abs(self):
		block = AbsBlock("")
		self.model.addBlock(block)
		return block, 1

	def root(self):
		block = RootBlock("")
		self.model.addBlock(block)
		return block, 2

	def sqrt(self):
		two = ConstantBlock("", 2.0)
		block = RootBlock("")
		self.model.addBlock(two)
		self.model.addBlock(block)
		self.model.addConnection(two, block, input_port_name="IN2")
		return block, 1

	def clamp(self):
		block = ClampBlock("", use_const=False)
		self.model.addBlock(block)
		return block, 3

	sat = clamp

	def mux(self):
		block = MultiplexerBlock("")
		self.model.addBlock(block)
		return block, 3, {"IN3": "select"}

	def d(self):
		block = DelayBlock("")
		self.model.addBlock(block)
		return block, 2, {"IN2": "IC"}

	def i(self):
		block = IntegratorBlock("")
		self.model.addBlock(block)
		return block, 3, {"IN2": "IC", "IN3": "delta_t"}

	def der(self):
		block = DerivatorBlock("")
		self.model.addBlock(block)
		return block, 3, {"IN2": "IC", "IN3": "delta_t"}


class EqTransformer(Transformer):
	"""
	Transforms the AST into a CBD model.

	Args:
		model:  The CBD model to start from. When :code:`None`, a
				new model will be created. Defaults to :code:`None`.
	"""
	# TODO: multiple output ports?
	# TODO: constant folding
	def __init__(self, model=None):
		super().__init__()
		self.model = CBD("") if model is None else model
		self.functions = EqFunctions(self.model)
		self.vars = {}
		self.var_results = {}
		self.nocollapse = set()

	def link(self, what, to, opn=None, ipn=None):
		if isinstance(what, Token) and what.type == "VNAME":
			self.linkVar(what.value, (to, ipn))
		else:
			self.model.addConnection(what, to, input_port_name=ipn, output_port_name=opn)

	def linkVar(self, name, to):
		self.vars[name].append(to)

	def start(self, _):
		all_vars = set(self.vars.keys())
		output_vars = set(self.var_results.keys())
		input_vars = all_vars - output_vars
		for inp in input_vars:
			self.model.addInputPort(inp)
			self.var_results[inp] = inp
		for var, cons in self.vars.items():
			from_ = self.var_results[var]
			for con, ipn in cons:
				self.model.addConnection(from_, con, input_port_name=ipn, output_port_name=None)
		return self.model

	def eqn(self, items):
		return items[0]

	def stmt(self, items):
		vname = items[0].value
		self.var_results[vname] = items[2]
		if items[1].value == "=":
			self.model.addOutputPort(vname)
			self.model.addConnection(items[2], vname)
		return items[2]

	def poper(self, items):
		self.nocollapse.add(items[0].getBlockName())
		return items[0]

	def sum(self, items):
		if len(items) > 1:
			N = ((len(items) - 1) // 2) + 1
			block = AdderBlock("", N)
			self.model.addBlock(block)
			self.link(items[0], block)
			for i in range(N - 1):
				idx = (i * 2) + 1
				if items[idx].type == "ADD":
					self.link(items[idx+1], block)
				else:
					neg = self.neg(["-", items[idx+1]])
					self.link(neg, block)
			return block
		return items[0]

	def prod(self, items):
		if len(items) > 1:
			N = ((len(items) - 1) // 2) + 1
			block = ProductBlock("", N)
			self.model.addBlock(block)
			self.link(items[0], block)
			for i in range(N - 1):
				idx = (i * 2) + 1
				if items[idx].type == "MUL":
					self.link(items[idx+1], block)
				elif items[idx].type == "DIV":
					inv = self.inv(["/", items[idx+1]])
					self.link(inv, block)
			return block
		return items[0]

	def pow(self, items):
		if len(items) > 1:
			block = PowerBlock("")
			self.model.addBlock(block)
			self.link(items[0], block)
			if len(items) == 3:
				self.link(items[2], block, ipn="IN2")
			return block
		return items[0]

	def mod(self, items):
		block = ModuloBlock("")
		self.model.addBlock(block)
		self.link(items[0], block)
		self.link(items[2], block, ipn="IN2")
		return block

	def neg(self, items):
		if isinstance(items[1], ConstantBlock) \
				and items[1].getBlockName() not in self.nocollapse:
			items[1].setValue(-items[1].getValue())
			return items[1]
		block = NegatorBlock("")
		self.model.addBlock(block)
		self.link(items[1], block)
		return block

	def not_(self, items):
		block = NotBlock("")
		self.model.addBlock(block)
		self.link(items[1], block)
		return block

	def delay(self, items):
		block = DelayBlock("")
		self.model.addBlock(block)
		self.link(items[0], block)
		return block

	def inv(self, items):
		if isinstance(items[1], ConstantBlock) \
				and items[1].getBlockName() not in self.nocollapse:
			items[1].setValue(1. / items[1].getValue())
			return items[1]
		block = InverterBlock("")
		self.model.addBlock(block)
		self.link(items[1], block)
		return block

	def var(self, items):
		return items[0]

	def func(self, items):
		fname = items[0].value.lower()
		args = items[1:]
		if self.functions._has_func(fname):
			vals = getattr(self.functions, fname)()
			block = vals[0]
			acnt = vals[1]
			mapper = {} if len(vals) == 2 else vals[2]
			if acnt > len(args):
				raise ParseError("Function '%s' has too few arguments (got %d, expected %d); "
				                 "at line %d, column %d" % (fname, len(args), acnt, items[0].line, items[0].end_column))
			if acnt < len(args):
				raise ParseError("Function '%s' has too many arguments (got %d, expected %d); "
				                 "at line %d, column %d" % (fname, len(args), acnt, items[0].line, items[0].end_column))
			for i, arg in enumerate(args):
				self.link(arg, block, ipn=mapper.get("IN%d" % (i+1), "IN%d" % (i+1)))
			return block
		if not hasattr(math, fname):
			raise ParseError("Function '%s' does not exist at line %d, column %d" \
			                    % (fname, items[0].line, items[0].end_column))
		if len(args) > 1:
			raise ParseError("Function '%s' has too many arguments (got %d, expected 1); "
			                 "at line %d, column %d" % (fname, len(args), items[0].line, items[0].end_column))
		block = GenericBlock("", fname)
		self.model.addBlock(block)
		self.link(args[0], block)
		return block

	def bool(self, items):
		oper = items[1].value
		first, second = items[0], items[2]
		if oper == "==":
			block = EqualsBlock("")
		elif oper == "<=":
			block = LessThanOrEqualsBlock("")
		elif oper == "<":
			block = LessThanBlock("")
		elif oper == ">=":
			block = LessThanOrEqualsBlock("")
			first, second = second, first
		elif oper == ">":
			block = LessThanBlock("")
			first, second = second, first
		elif oper in ["or", "||"]:
			block = OrBlock("")
		elif oper in ["and", "&&"]:
			block = AndBlock("")
		else:
			raise ValueError("Impossible condition: uncaught, invalid boolean operator!")

		self.model.addBlock(block)
		self.link(first, block, ipn="IN1")
		self.link(second, block, ipn="IN2")
		return block

	def VNAME(self, tok):
		vname = tok.value
		if vname == "time":
			block = TimeBlock("")
			self.model.addBlock(block)
			return block
		if self.functions._has_func(vname):
			raise ParseError("Invalid variable name '%s' at line %d, column %d" \
			                 % (vname, items[0].line, items[0].end_column))
		if vname not in self.vars:
			self.vars[vname] = []
		return tok

	def NUMBER(self, tok):
		block = ConstantBlock("", float(tok.value))
		self.model.addBlock(block)
		return block


if __name__ == '__main__':
	from pyCBD.converters.CBDDraw import gvDraw

	parser = eq2CBD()
	gvDraw(parser.parse("x := 7 + 6"), "test.dot")
