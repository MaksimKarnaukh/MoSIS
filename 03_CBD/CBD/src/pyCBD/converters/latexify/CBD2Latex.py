from pyCBD.converters.latexify.functions import BLOCK_MAP as _BLOCK_MAP
from pyCBD.converters.latexify.functions import *


# TODO: memory blocks
class CBD2Latex:
	"""
	Creates a corresponding set of LaTeX-equations for a CBD model.

	Args:
		model (pyCBD.Core.CBD): The model to create the equations for.

	Keyword Arguments:
		show_steps (bool):      When :code:`True`, all intermediary steps will
								be shown. Defaults to :code:`False`.
		ignore_path (bool):     When :code:`True`, the name of the original model
								will be removed from all path names. This name is
								a common prefix over the system.
								Defaults to :code:`True`.
		escape_nonlatex (bool): When :code:`True`, non-latex characters (e.g., underscores)
								are escaped from the rendered result, if rendered as LaTeX.
								Defaults to :code:`True`.
		time_variable (str):    The name for the variable that represents the time
								(i.e., the current iteration). Defaults to :code:`'i'`.
		render_latex (bool):    When :code:`True`, the :func:`render` method will
								output a latex-formatted string. Otherwise, simple
								text formatting is done. Defaults to :code:`True`.
		time_format (str):      How the time must be formatted when rendered. By default,
								it will be placed in parentheses at the end. Use
								:code:`{time}` to identify the time constant.
		delta_t (str):          Representation of the used delta in the render. This will
								be appended to values that have been computed for a delay
								block. This is only to be used when the time does not
								identify the iteration, but the actual simulation time.
								Defaults to :code:`'i'`.
		replace_par (bool):     When :code:`True`, the parentheses will be replaced by the
								much cleaner :code:`\\left(` and :code:`\\right)`, if rendered
								in LaTeX-format. Defaults to :code:`True`.
		type_formats (dict):    A dictionary of :code:`{ operationType -> callable }` that
								allows for the remapping of mathematical descriptions based,
								where :code:`operationType` identifies the operation to remap
								and :code:`callable` a function that takes the name/symbol and
								the arguments as input and produces a list of function objects.

								See Also:
									:attr:`pyCBD.converters.latexify.functions.BLOCK_MAP`.
		path_sep (str):         The separator to use for the paths. Defaults to :code:`"."`.
		path_prefix (str):      The prefix to use for the paths. Defaults to the empty string.
		ignore (iterable):      A list of block classes not to flatten.
	"""

	DEFAULT_CONFIG = {
		"show_steps": False,
		"ignore_path": True,
		"escape_nonlatex": True,
		"time_variable": 'i',
		"render_latex": True,
		"time_format": "({time})",
		"delta_t": "i",
		"replace_par": True,
		"type_formats": {},
		"path_sep": '.',
		"path_prefix": '',
		"ignore": []
	}
	"""Default configuration setup."""

	def __init__(self, model, **kwargs):
		self.config = self.DEFAULT_CONFIG
		for k in kwargs:
			if k in self.config:
				self.config[k] = kwargs[k]

		self.model = model.flattened(ignore=self.config["ignore"])

		self.equations = []
		self.outputs = [self._rename(self.model.getPath(self.config['path_sep']) + self.config['path_sep'] + x) for x in self.model.getSignals().keys()]
		assert len(self.outputs) > 0, "Cannot create latex representation without outputs."
		self._collect_equations()
		self._step = 0

	def _rename(self, name):
		return CBD2Latex.rename(name, self.config, self.model)

	@staticmethod
	def rename(name, config, model):
		"""Makes the name of a path accurate.

		Args:
			name (str):     The name to convert.
			config (dict):  Configuration dictionary (see above).
			model (CBD):    The parent pyCBD model.
		"""
		if config["ignore_path"]:
			mname = model.getPath(config['path_sep']) + config['path_sep']
			if name.startswith(mname):
				name = name[len(mname):]
		name = name.replace("-", "_")
		if config["render_latex"] and config["escape_nonlatex"]:
			name = name.replace("_", r"\_")
		return config["path_prefix"] + name

	def get_block_equation(self, block):
		inputs = [self._rename(block.getPath(self.config["path_sep"]) + self.config['path_sep'] + x) for x in block.getInputPortNames()]
		bdata = self.config["type_formats"].get(block.getBlockType(), _BLOCK_MAP.get(block.getBlockType(), lambda b: [Fnc(b.getFunctionName())]))
		fncs = bdata(block)
		for f in fncs:
			f.args = [VarFnc(x) for x in inputs]
		eqs = []
		outputs = [self._rename(block.getPath(self.config["path_sep"]) + self.config['path_sep'] + x) for x in block.getOutputPortNames()]
		for i, fnc in enumerate(fncs):
			eqs.append(Eq(outputs[i], fnc))
		return eqs

	def _collect_equations(self):
		"""
		Loads the equations from the model in.

		See Also:
			`Cláudio Gomes, Joachim Denil and Hans Vangheluwe. 2016. "Causal-Block Diagrams",
			Technical Report <https://repository.uantwerpen.be/docman/irua/d28eb1/151279.pdf>`_
		"""
		# Add all blocks
		for block in self.model.getBlocks():
			eq = self.get_block_equation(block)
			for e in eq:
				self.equations.append(e)

		# Add all connections
		for block in self.model.getBlocks():
			path = block.getPath(self.config['path_sep'])
			for in_port in block.getInputPorts():
				out_port = in_port.getIncoming().source
				v_path = self._rename(out_port.block.getPath(self.config['path_sep']) + self.config['path_sep'] + out_port.name)
				lhs = self._rename(path + self.config['path_sep'] + in_port.name)
				rhs = VarFnc(v_path)
				self.equations.append(Eq(lhs, rhs))

		# Add all outputs
		for port in self.model.getOutputPorts():
			prev = port.getIncoming().source
			p_path = self._rename(
				prev.block.getPath(self.config['path_sep']) + self.config['path_sep'] + prev.name)
			n_path = self._rename(
				port.block.getPath(self.config['path_sep']) + self.config['path_sep'] + port.name)
			self.equations.append(Eq(n_path, VarFnc(p_path)))

	def render(self, rl=None):
		"""
		Creates the LaTeX string for the model, based on the current level of simplifications.

		Args:
			rl (bool):      Identifies if the rendering must result in a LaTeX-renderable string.
							This argument basically overwrites the :attr:`render_latex` config
							attribute. When :code:`None`, the value from the config is used.
							Defaults to :code:`None`.
		"""
		if rl is None:
			rl = self.config["render_latex"]
		if rl:
			lat = self.latex()
			if self.config["replace_par"]:
				lat = lat.replace("(", "\\left(").replace(")", "\\right)")
			return "\\left\\{\\begin{array}{lcl}\n%s\\end{array}\\right." % lat
		return self.eq()

	def eq(self, time=Time.now()):
		"""
		Obtains the current set of equations in a format that can be parsed by
		the :mod:`pyCBD.converters.eq2CBD` converter.
		This allows model simplifications and optimizations.

		Args:
			time (Time):    The time at which to obtain the equations.
		"""
		res = ""
		for eq in self.equations:
			eqs = eq.at(time)
			for e in eqs:
				eq_time_fmt, time_fmt = self._get_time_formats(e)
				res += e.eq().format(T=time_fmt, E=eq_time_fmt, dt=self.config["delta_t"]) + '\n'
		return res

	def latex(self):
		"""
		Obtains the current set of equations in LaTeX format.
		"""
		res = ""
		for eq in self.equations:
			eqs = eq.at(Time.now())
			for e in eqs:
				eq_time_fmt, time_fmt = self._get_time_formats(e)
				res += e.latex().format(T=time_fmt, E=eq_time_fmt, dt=self.config["delta_t"]) + '\\\\\n'
		return res

	def _get_time_formats(self, e):
		dt = self.config["delta_t"]
		if dt != "":
			dt = " * " + dt
		time_fmt = self.config["time_format"].format(time=str(e.rhs.time)).format(
			i=self.config["time_variable"], dt=dt)
		eq_time_fmt = self.config["time_format"].format(time=str(e.rhs.eq_time)).format(
			i=self.config["time_variable"], dt=dt)
		return eq_time_fmt, time_fmt

	def simplify_links(self):
		"""
		First step to execute is a link simplification. Generally, there are more links
		than blocks, so this function will take care of the largest simplification.
		"""
		links = set()
		numeric = set()

		for ix, eq in enumerate(self.equations):
			if isinstance(eq.rhs, ConstantFnc):
				numeric.add(ix)
			elif isinstance(eq.rhs, VarFnc):
				links.add(ix)

		for ix in links:
			for eq in self.equations:
				eq.apply(self.equations[ix])

		for i, eq in enumerate(self.equations):
			for ix in numeric:
				if i == ix: continue
				eq.apply(self.equations[ix])

		for ix in reversed(sorted(list(numeric | links))):
			if self.equations[ix].lhs not in self.outputs:
				self.equations.pop(ix)

	def substitute(self):
		"""
		Combines multiple equations into one, based on the requested output, by
		means of substitution. This function will be called multiple times: once
		for each "step" in the simplification.

		See Also:
			:func:`simplify`
		"""
		_MEMORY = ["D"]
		outputs = self.outputs[:]
		for e in self.equations:
			if e.rhs.name in _MEMORY:
				outputs.append(e.lhs)
		to_delete = set()
		for output in outputs:
			oeq = None
			for eq in self.equations:
				if eq.lhs == output:
					oeq = eq
					break
			if oeq is None: continue
			deps = oeq.get_dependencies()
			deqs = []
			for d in deps:
				if d.name in self.outputs: continue
				for eq in self.equations:
					if eq.lhs == d.name:
						deqs.append(eq)
			for deq in deqs:
				# prevent cyclic dependency
				# TODO: maybe refactor part of the equation?
				if deq.rhs.contains(deq.lhs):
					continue
				if deq.lhs not in outputs:
					oeq.apply(deq)
					to_delete.add(deq.lhs)

		# simplify functions
		neq = []
		for eq in self.equations:
			neq += eq.simplify()
		self.equations = neq

		# TODO: check no removal of outputs?
		# Remove obsolete equations
		tdl = None
		while tdl is None or to_delete != tdl:
			tdl = to_delete.copy()
			for eq in self.equations:
				if eq.lhs in to_delete: continue
				deps = set([x.name for x in eq.get_dependencies()])
				to_delete -= deps

		tdix = []
		for ix, eq in enumerate(self.equations):
			if eq.lhs in to_delete and eq.lhs not in self.outputs:
				tdix.append(ix)
		for ix in reversed(tdix):
			self.equations.pop(ix)

	def simplify(self, steps=-1):
		"""
		Simplifies the system of equations to become a more optimal solution.

		Args:
			steps (int):        When positive, this indicates the amount of steps
								that must be taken. When negative, the equations
								will be simplified until a convergence (i.e. no
								possible changes) is reached. Defaults to -1.

		See Also:
			- :func:`simplify_links`
			- :func:`substitute`
		"""
		if self.config["show_steps"]:
			self._trace("INITIAL SYSTEM")
		self.simplify_links()
		txt = " substituted all connections and constant values"
		peq = ""
		i = 0
		while peq != self.eq():
			if 0 <= steps <= i: break
			peq = self.eq()
			if self.config["show_steps"]:
				self._trace(txt)
			self.substitute()
			i += 1
			txt = ""

	def _trace(self, text=""):
		"""Traces a step in the solution.

		Args:
			text (str): Additional text to print.
		"""
		if self._step == 0:
			print("" + text + ":")
		else:
			print("STEP %d:" % self._step, text)
		print(self.render())
		self._step += 1


if __name__ == '__main__':
	from pyCBD.Core import CBD
	from pyCBD.lib.std import AdderBlock, ConstantBlock, InverterBlock, ProductBlock, DelayBlock
	from pyCBD.converters.CBDDraw import gvDraw

	model = CBD("root", [], ["x"])
	model.addBlock(ConstantBlock("C2", 2))
	model.addBlock(DelayBlock("delay1"))
	model.addBlock(DelayBlock("delay2"))
	# model.addBlock(ConstantBlock("C3", 3))
	model.addBlock(ConstantBlock("C4", 4))
	# model.addBlock(AdderBlock("sum"))
	# model.addBlock(ProductBlock("prod"))
	# model.addBlock(ProductBlock("div"))
	# model.addBlock(InverterBlock("inv"))
	#
	# model.addConnection("C2", "sum")
	# model.addConnection("prod", "sum")
	# model.addConnection("sum", "div")
	# model.addConnection("sum", "x")
	# model.addConnection("C4", "inv")
	# model.addConnection("inv", "div")
	# model.addConnection("div", "y")
	# model.addConnection("div", "prod")
	# model.addConnection("C3", "prod")
	# model.addConnection("C2", "delay", input_port_name="IC")
	# model.addConnection("x", "delay", input_port_name="IN1")
	# model.addConnection("delay", "y")

	model.addConnection("delay1", "delay2")
	model.addConnection("delay2", "delay1")
	model.addConnection("C2", "delay1", input_port_name="IC")
	model.addConnection("C4", "delay2", input_port_name="IC")
	model.addConnection("delay2", "x")
	c2l = CBD2Latex(model, show_steps=True, render_latex=False)

	gvDraw(model, "test.gv")

	c2l.simplify()

