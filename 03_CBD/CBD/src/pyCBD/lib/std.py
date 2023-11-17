"""
This file contains the standard library for CBD building blocks.
"""
from pyCBD.Core import BaseBlock, CBD
import math

__all__ = ['ConstantBlock', 'NegatorBlock', 'InverterBlock',
           'AdderBlock', 'ProductBlock',
           'ModuloBlock', 'RootBlock', 'PowerBlock',
           'AbsBlock', 'IntBlock', 'ClampBlock',
           'GenericBlock',
           'MinBlock', 'MaxBlock',
           'LessThanBlock', 'EqualsBlock', 'LessThanOrEqualsBlock',
           'NotBlock', 'OrBlock', 'AndBlock',
           'MultiplexerBlock', 'SplitBlock',
           'DelayBlock', 'DeltaTBlock', 'TimeBlock', 'LoggingBlock',
           'AddOneBlock', 'DerivatorBlock', 'IntegratorBlock',
           'Clock', 'SequenceBlock']

class ConstantBlock(BaseBlock):
	"""
	The constant block will always output its constant value.

	Arguments:
		block_name (str):   The name of the block.
		value (float):      The constant value of the block.

	:Output Ports:
		**OUT1** -- The (current) constant value.

	Note:
		This value may be "tuned" during a simulation, making
		it variable through time.
	"""
	def __init__(self, block_name, value=0.0):
		BaseBlock.__init__(self, block_name, [], ["OUT1"])
		self.__value = value

	def getValue(self):
		"""Obtains the current value."""
		return self.__value

	def setValue(self, value):
		"""Alters the constant value."""
		self.__value = value

	def compute(self, curIteration):
		self.appendToSignal(self.getValue())

	def __repr__(self):  # pragma: no cover
		return BaseBlock.__repr__(self) + "  Value = " + str(self.getValue()) + "\n"


class NegatorBlock(BaseBlock):
	"""
	The negator will output the value of the input multiplied with -1.

	Arguments:
		block_name (str):   The name of the block.

	:Input Ports:
		**IN1** -- The value to be negated.

	:Output Ports:
		**OUT1** -- The negated value.
	"""
	def __init__(self, block_name):
		BaseBlock.__init__(self, block_name, ["IN1"], ["OUT1"])

	def compute(self, curIteration):
		self.appendToSignal(-self.getInputSignal(curIteration, "IN1").value)


class InverterBlock(BaseBlock):
	"""
	The inverter will output the input's inverse.

	Arguments:
		block_name (str):   The name of the block.
		tolerance (float):  The maximal value when to throw a :code:`ZeroDivisionError`.
							When the input is larger than :code:`tolerance`, no error
							will be thrown. Defaults to :code:`1e-30`.

	:Input Ports:
		**IN1** -- The value to be inverted.

	:Output Ports:
		**OUT1** -- The inverted value.

	Raises:
		ZeroDivisionError: When the input is less than :code:`tolerance`.
	"""
	def __init__(self, block_name, tolerance=1e-30):
		BaseBlock.__init__(self, block_name, ["IN1"], ["OUT1"])
		self._tolerance = tolerance

	def compute(self, curIteration):
		input = self.getInputSignal(curIteration, "IN1").value
		if abs(input) < self._tolerance:
			raise ZeroDivisionError("InverterBlock '{}' received input less than {}.".format(self.getPath(), self._tolerance))
		self.appendToSignal(1.0 / input)


class GainBlock(BaseBlock):
	"""
	The gain will output the input, multiplied by a constant.

	Arguments:
		block_name (str):   The name of the block.
		value (numeric):    The value of the block.

	:Input Ports:
		**IN1** -- The value to be multiplied.

	:Output Ports:
		**OUT1** -- The multiplied value.
	"""
	def __init__(self, block_name, value):
		BaseBlock.__init__(self, block_name, ["IN1"], ["OUT1"])
		self._value = value

	def compute(self, curIteration):
		input = self.getInputSignal(curIteration, "IN1").value
		self.appendToSignal(input * self._value)


class AdderBlock(BaseBlock):
	"""
	The adderblock will add all the inputs.

	Args:
		block_name (str):       The name of the block.
		numberOfInputs (int):   The amount of input ports.

	:Input Ports:
		- **IN1** -- The first addendend.
		- **IN2** -- The second addendend.
		- ...

	:Output Ports:
		**OUT1** -- The sum of all inputs.
	"""
	def __init__(self, block_name, numberOfInputs=2):
		BaseBlock.__init__(self, block_name, ["IN%d" % (x+1) for x in range(numberOfInputs)], ["OUT1"])
		self.__numberOfInputs = numberOfInputs

	def compute(self, curIteration):
		result = 0
		for i in range(1, self.__numberOfInputs+1):
			result += self.getInputSignal(curIteration, "IN%d"%i).value
		self.appendToSignal(result)

	def getNumberOfInputs(self):
		"""
		Gets the total number of input ports.
		"""
		return self.__numberOfInputs


class ProductBlock(BaseBlock):
	"""
	The product block will multiply all the inputs.

	Args:
		block_name (str):       The name of the block.
		numberOfInputs (int):   The amount of input ports.

	:Input Ports:
		- **IN1** -- The first factor.
		- **IN2** -- The second factor.
		- ...

	:Output Ports:
		**OUT1** -- The product of all inputs.
	"""
	def __init__(self, block_name, numberOfInputs=2):
		BaseBlock.__init__(self, block_name, ["IN%d" % (x+1) for x in range(numberOfInputs)], ["OUT1"])
		self.__numberOfInputs = numberOfInputs

	def compute(self, curIteration):
		result = 1
		for i in range(1, self.__numberOfInputs+1):
			result *= self.getInputSignal(curIteration, "IN%d"%i).value
		self.appendToSignal(result)

	def getNumberOfInputs(self):
		"""
		Gets the total number of input ports.
		"""
		return self.__numberOfInputs


class ModuloBlock(BaseBlock):
	"""
	A basic block that computes the modulo division, w.r.t. the C-standard.

	Args:
		block_name (str):       The name of the block.

	:Input Ports:
		- **IN1** -- The dividend.
		- **IN2** -- The divisor.

	:Output Ports:
		**OUT1** -- The remainder after division.

	See Also:
		`math.fmod <https://docs.python.org/3.8/library/math.html#math.fmod>`_
	"""
	def __init__(self, block_name):
		BaseBlock.__init__(self, block_name, ["IN1", "IN2"], ["OUT1"])

	def compute(self, curIteration):
		# Use 'math.fmod' for validity with C w.r.t. negative values AND floats
		self.appendToSignal(math.fmod(self.getInputSignal(curIteration, "IN1").value, self.getInputSignal(curIteration, "IN2").value))

	def defaultInputPortNameIdentifier(self):
		raise ValueError("The order of the operands is important for this block. Please provide a port name.")


class RootBlock(BaseBlock):
	"""
	A basic block that computes the :code:`IN2`-th root of :code:`IN1`.
	Hence,

	.. math::
		OUT1 = \\sqrt[IN2]{IN1}

	Args:
		block_name (str):   The name of the block.
		tolerance (float):  The maximal value when to throw a :code:`ZeroDivisionError`.
							When the input is larger than :code:`tolerance`, no error
							will be thrown. Defaults to :code:`1e-30`.

	:Input Ports:
		- **IN1** -- The radicand.
		- **IN2** -- The root index.

	:Output Ports:
		**OUT1** -- The :code:`IN2`-th root of :code:`IN1`.

	Raises:
		ZeroDivisionError: When the input is less than :code:`tolerance`.
	"""
	def __init__(self, block_name, tolerance=1e-30):
		BaseBlock.__init__(self, block_name, ["IN1", "IN2"], ["OUT1"])
		self._tolerance = tolerance

	def compute(self, curIteration):
		input = self.getInputSignal(curIteration, "IN2").value
		if abs(input) < self._tolerance:
			raise ZeroDivisionError("RootBlock '{}' received input less than {}.".format(self.getPath(), self._tolerance))
		self.appendToSignal(self.getInputSignal(curIteration, "IN1").value ** (1 / input))

	def defaultInputPortNameIdentifier(self):
		raise ValueError("The order of the operands is important for this block. Please provide a port name.")


class PowerBlock(BaseBlock):
	"""
	A basic block that computes the :code:`IN2`-th power of :code:`IN1`.
	Hence,

	.. math::
		OUT1 = IN1^{IN2}

	Args:
		block_name (str):   The name of the block.

	:Input Ports:
		- **IN1** -- The base.
		- **IN2** -- The exponent.

	:Output Ports:
		**OUT1** -- The :code:`IN2`-th power of :code:`IN1`.
	"""
	def __init__(self, block_name):
		BaseBlock.__init__(self, block_name, ["IN1", "IN2"], ["OUT1"])

	def compute(self, curIteration):
		self.appendToSignal(self.getInputSignal(curIteration, "IN1").value ** self.getInputSignal(curIteration, "IN2").value)

	def defaultInputPortNameIdentifier(self):
		raise ValueError("The order of the operands is important for this block. Please provide a port name.")


class AbsBlock(BaseBlock):
	"""
	The abs block will output the absolute value of the input.

	Args:
		block_name (str):   The name of the block.

	:Input Ports:
		**IN1** -- The input.

	:Output Ports:
		**OUT1** -- The absolute value of the input.
	"""
	def __init__(self, block_name):
		BaseBlock.__init__(self, block_name, ["IN1"], ["OUT1"])

	def compute(self, curIteration):
		self.appendToSignal(abs(self.getInputSignal(curIteration).value))


class IntBlock(BaseBlock):
	"""
	The int block will output the integer value (floored) of the input.

	Args:
		block_name (str):   The name of the block.

	:Input Ports:
		**IN1** -- The input.

	:Output Ports:
		**OUT1** -- The integer (i.e., floored) value of the input.
	"""
	def __init__(self, block_name):
		BaseBlock.__init__(self, block_name, ["IN1"], ["OUT1"])

	def compute(self, curIteration):
		self.appendToSignal(int(self.getInputSignal(curIteration).value))


class ClampBlock(BaseBlock):
	"""
	The clamp block will clamp the input between :code:`min` and :code:`max`.
	A :code:`clamp` function is sometimes also known as a :code:`limiter` or
	:code:`saturation` function.

	Args:
		block_name (str):   The name of the block.
		min (numeric):      The minimal value.
		max (numeric):      The maximal value.
		use_const (bool):   When :code:`True`, the :attr:`min` and :attr:`max`
							values will be used. Otherwise, the minimal and
							maximal values are expected as inputs 2 and 3,
							respectively.

	:Input Ports:
		- **IN1** -- The signal to clamp.
		- **IN2** -- The minimal value. Only available when :code:`use_const`
		  is :code:`True`.
		- **IN3** -- The maximal value. Only available when :code:`use_const`
		  is :code:`True`.

	:Output Ports:
		**OUT1** -- The clamped value.
	"""
	def __init__(self, block_name, min=-1, max=1, use_const=True):
		BaseBlock.__init__(self, block_name, ["IN1"] if use_const else ["IN1", "IN2", "IN3"], ["OUT1"])
		self._use_const = use_const
		self.min = min
		self.max = max

	def compute(self, curIteration):
		if self._use_const:
			min_ = self.min
			max_ = self.max
		else:
			min_ = self.getInputSignal(curIteration, "IN2").value
			max_ = self.getInputSignal(curIteration, "IN3").value
		x = self.getInputSignal(curIteration, "IN1").value
		self.appendToSignal(min(max(x, min_), max_))

	def defaultInputPortNameIdentifier(self):
		if not self._use_const:
			raise ValueError("The order of the operands is important for this block. Please provide a port name.")
		return super(ClampBlock, self).defaultInputPortNameIdentifier()


class GenericBlock(BaseBlock):
	"""
	The generic block will evaluate an operator on the input.

	Args:
		block_name (str):       The name of the block.
		block_operator (str):   The name (string) of a single-argument Python
								function that is available in the :mod:`math`
								module. Defaults to :code:`None`.

	:Input Ports:
		**IN1** -- The signal to transform.

	:Output Ports:
		**OUT1** -- The input to which the operation was applied.

	Note:
		Multi-argument functions cannot be used.

	Warning:
		When the CBD model is exported to be used in another simulator (e.g.,
		FMUs, plain C...), it is possible the function does not exist in the
		corresponding mathematics libraries. It is up to the user to ensure
		correctness in this case.

	See Also:
		`Python math module <https://docs.python.org/3.8/library/math.html>`_
	"""
	def __init__(self, block_name, block_operator=None):
		# operator is the name (a string) of a Python function from the math library
		BaseBlock.__init__(self, block_name, ["IN1"], ["OUT1"])
		self.__block_operator = block_operator

	def getBlockOperator(self):
		"""
		Obtains the block operator.
		"""
		return self.__block_operator

	def compute(self, curIteration):
		a = self.getInputSignal(curIteration, "IN1").value
		self.appendToSignal(getattr(math, self.getBlockOperator())(a))

	def __repr__(self):  # pragma: no cover
		repr = BaseBlock.__repr__(self)
		if self.__block_operator is None:
			repr += "  No operator given\n"
		else:
			repr += "  Operator :: " + self.__block_operator + "\n"
		return repr


class MultiplexerBlock(BaseBlock):
	"""
	The multiplexer block will output the signal from an input, based on the index
	:code:`select`.

	Args:
		block_name (str):       The name of the block.
		numberOfInputs (int):   The amount of input ports to choose from. Defaults to 2.
		zero (bool):            When :code:`True`, the index is zero-based. Otherwise,
								the :code:`select` signal is interpreted as 1-indexed.
								Defaults to :code:`True`.

	:Input Ports:
		- **select** -- The input index to choose from. When out of range, an exception
		  is thrown.
		- **IN1** -- The first option.
		- **IN2** -- The second option.
		- ...

	:Output Ports:
		**OUT1** -- The input to which the operation was applied.

	Raises:
		IndexError: When the :code:`select` input is out of range.

	Note:
		This block is not optimized in the simulator. Even though there can be a part of the
		block that is not necessary to be computed, the dependency graph still includes both
		inputs. While this is a definite optimization, recomputing the dependency graph at
		each iteration is much less ideal.
	"""
	def __init__(self, block_name, numberOfInputs=2, zero=True):
		BaseBlock.__init__(self, block_name, ["select"] + ["IN%i" % (x + 1) for x in range(numberOfInputs)], ["OUT1"])
		self.__numberOfInputs = numberOfInputs
		self.__zero = zero

	def compute(self, curIteration):
		select = self.getInputSignal(curIteration, "select").value
		if self.__zero:
			select += 1
		if select < 0 or select > self.__numberOfInputs:
			raise IndexError("Select input out of range for block %s" % self.getPath())
		self.appendToSignal(self.getInputSignal(curIteration, "IN%d" % select).value)

	def getNumberOfInputs(self):
		"""
		Gets the number of input ports to choose from.
		"""
		return self.__numberOfInputs

	def defaultInputPortNameIdentifier(self):
		raise ValueError("The order of the operands is important for this block. Please provide a port name.")


class MinBlock(BaseBlock):
	"""
	The min block will output the minimal value of all its inputs.

	Args:
		block_name (str):       The name of the block.
		numberOfInputs (int):   The amount of input ports. Defaults to 2.

	:Input Ports:
		- **IN1** -- The first input.
		- **IN2** -- The second input.
		- ...

	:Output Ports:
		**OUT1** -- The minimal value of all inputs.
	"""
	def __init__(self, block_name, numberOfInputs=2):
		BaseBlock.__init__(self, block_name, ["IN%d" % (x+1) for x in range(numberOfInputs)], ["OUT1"])
		self.__numberOfInputs = numberOfInputs

	def compute(self, curIteration):
		result = []
		for i in range(1, self.__numberOfInputs+1):
			result.append(self.getInputSignal(curIteration, "IN%d"%i).value)
		self.appendToSignal(min(result))

	def getNumberOfInputs(self):
		"""
		Gets the total number of input ports.
		"""
		return self.__numberOfInputs


class MaxBlock(BaseBlock):
	"""
	The max block will output the maximal value of all its inputs.

	Args:
		block_name (str):       The name of the block.
		numberOfInputs (int):   The amount of input ports. Defaults to 2.

	:Input Ports:
		- **IN1** -- The first input.
		- **IN2** -- The second input.
		- ...

	:Output Ports:
		**OUT1** -- The maximal value of all inputs.
	"""
	def __init__(self, block_name, numberOfInputs=2):
		BaseBlock.__init__(self, block_name, ["IN%d" % (x+1) for x in range(numberOfInputs)], ["OUT1"])
		self.__numberOfInputs = numberOfInputs

	def compute(self, curIteration):
		result = []
		for i in range(1, self.__numberOfInputs+1):
			result.append(self.getInputSignal(curIteration, "IN%d"%i).value)
		self.appendToSignal(max(result))

	def getNumberOfInputs(self):
		"""
		Gets the total number of input ports.
		"""
		return self.__numberOfInputs


class SplitBlock(BaseBlock):
	"""
	The split block will split a signal over multiple paths.
	While this block can generally be omitted, it may still be used for clarity
	and clean-ness of the models.

	Args:
		block_name (str):       The name of the block.
		numberOfOutputs (int):  The amount of paths to split into. Defaults to 2.

	:Input Ports:
		**IN1** -- The signal.

	:Output Ports:
		- **OUT1** -- The first output.
		- **OUT2** -- The second output.
		- ...
	"""
	def __init__(self, block_name, numberOfOutputs=2):
		BaseBlock.__init__(self, block_name, ["IN1"], ["OUT%d" % (i+1) for i in range(numberOfOutputs)])
		self.__numberOfOutputs = numberOfOutputs

	def compute(self, curIteration):
		value = self.getInputSignal(curIteration).value
		for i in range(self.__numberOfOutputs):
			self.appendToSignal(value, "OUT%d" % (i+1))

	def getNumberOfOutputs(self):
		"""
		Gets the total number of output ports.
		"""
		return self.__numberOfOutputs


class LessThanBlock(BaseBlock):
	"""
	A simple block that will test if :code:`IN1` is smaller than :code:`IN2`.
	This block will output a *falsy* or *truthy* value (i.e., 0 or 1), based on the signal.

	Args:
		block_name (str):       The name of the block.

	:Input Ports:
		- **IN1** -- The value that will be tested to be smaller.
		- **IN2** -- The value that will be tested to be larger.

	:Output Ports:
		**OUT1** -- Yields a 1 when :code:`IN1` is smaller than :code:`IN2`, otherwise 0.
		In Python, 0 is a *falsy* value and can therefore be used as boolean check, or as computation
		value for other equation in the CBD. Similaryly, 1 is a *truthy* value.

	Tip:
		To check the "greater than" relationship, you can swap the :code:`IN1` and :code:`IN2` inputs
		around.

	See Also:
		`Truthy and Falsy values in Python <https://docs.python.org/3/library/stdtypes.html#truth-value-testing>`_
	"""
	def __init__(self, block_name):
		BaseBlock.__init__(self, block_name, ["IN1", "IN2"], ["OUT1"])

	def	compute(self, curIteration):
		gisv = lambda s: self.getInputSignal(curIteration, s).value
		self.appendToSignal(1 if gisv("IN1") < gisv("IN2") else 0)

	def defaultInputPortNameIdentifier(self):
		raise ValueError("The order of the operands is important for this block. Please provide a port name.")


class EqualsBlock(BaseBlock):
	"""
	A simple block that will test if :code:`IN1` equals :code:`IN2`.
	This block will output a *falsy* or *truthy* value (i.e., 0 or 1), based on the signal.

	Args:
		block_name (str):       The name of the block.

	:Input Ports:
		- **IN1** -- The first value.
		- **IN2** -- The second value.

	:Output Ports:
		**OUT1** -- Yields a 1 when :code:`IN1` equals :code:`IN2`, otherwise 0.
		In Python, 0 is a *falsy* value and can therefore be used as boolean check, or as computation
		value for other equation in the CBD. Similaryly, 1 is a *truthy* value.

	See Also:
		`Truthy and Falsy values in Python <https://docs.python.org/3/library/stdtypes.html#truth-value-testing>`_
	"""
	def __init__(self, block_name):
		BaseBlock.__init__(self, block_name, ["IN1", "IN2"], ["OUT1"])

	def	compute(self, curIteration):
		gisv = lambda s: self.getInputSignal(curIteration, s).value
		self.appendToSignal(1 if gisv("IN1") == gisv("IN2") else 0)


class LessThanOrEqualsBlock(BaseBlock):
	"""
	A simple block that will test if :code:`IN1` is smaller than or equal to :code:`IN2`.
	This block will output a *falsy* or *truthy* value (i.e., 0 or 1), based on the signal.

	Args:
		block_name (str):       The name of the block.

	:Input Ports:
		- **IN1** -- The value that will be tested to be smaller (or equal).
		- **IN2** -- The value that will be tested to be larger (or equal).

	:Output Ports:
		**OUT1** -- Yields a 1 when :code:`IN1` is smaller than or equal to :code:`IN2`, otherwise 0.
		In Python, 0 is a *falsy* value and can therefore be used as boolean check, or as computation
		value for other equation in the CBD. Similaryly, 1 is a *truthy* value.

	Tip:
		To check the "greater than or equal" relationship, you can swap the :code:`IN1` and :code:`IN2` inputs
		around.

	See Also:
		`Truthy and Falsy values in Python <https://docs.python.org/3/library/stdtypes.html#truth-value-testing>`_
	"""
	def __init__(self, block_name):
		BaseBlock.__init__(self, block_name, ["IN1", "IN2"], ["OUT1"])

	def	compute(self, curIteration):
		gisv = lambda s: self.getInputSignal(curIteration, s).value
		self.appendToSignal(1 if gisv("IN1") <= gisv("IN2") else 0)

	def defaultInputPortNameIdentifier(self):
		raise ValueError("The order of the operands is important for this block. Please provide a port name.")


class NotBlock(BaseBlock):
	"""
	A simple block that will (boolean) invert :code:`IN1`. This is similar to the :code:`not`
	operator in programming.
	This block expects a *falsy* or *truthy* value and outputs the (boolean) inverse.

	Args:
		block_name (str):       The name of the block.

	:Input Ports:
		**IN1** -- The value that will be (boolean) inverted.

	:Output Ports:
		**OUT1** -- Yields a 1 when :code:`IN1` is *falsy* and 0 when it's *truthy*.
		In Python, 0 is a *falsy* value and can therefore be used as boolean check, or as computation
		value for other equation in the CBD. Similaryly, 1 is a *truthy* value.

	See Also:
		`Truthy and Falsy values in Python <https://docs.python.org/3/library/stdtypes.html#truth-value-testing>`_
	"""
	def __init__(self, block_name):
		BaseBlock.__init__(self, block_name, ["IN1"], ["OUT1"])

	def	compute(self, curIteration):
		result = 0 if self.getInputSignal(curIteration, "IN1").value else 1
		self.appendToSignal(result)


class OrBlock(BaseBlock):
	"""
	A simple block that will apply the :code:`or` operator to multiple inputs.
	This block expects and returns *falsy* and/or *truthy* values.

	Args:
		block_name (str):       The name of the block.
		numberOfInputs (int):   The amount of inputs. Defaults to 2.

	:Input Ports:
		- **IN1** -- The first input.
		- **IN2** -- The second input.
		- ...

	:Output Ports:
		**OUT1** -- Yields a 1 when at least one of the inputs is *truthy*. Otherwise, 0.
		In Python, 0 is a *falsy* value and can therefore be used as boolean check, or as computation
		value for other equation in the CBD. Similaryly, 1 is a *truthy* value.

	See Also:
		`Truthy and Falsy values in Python <https://docs.python.org/3/library/stdtypes.html#truth-value-testing>`_
	"""
	def __init__(self, block_name, numberOfInputs=2):
		BaseBlock.__init__(self, block_name, ["IN%i" % (x + 1) for x in range(numberOfInputs)], ["OUT1"])
		self.__numberOfInputs = numberOfInputs

	def	compute(self, curIteration):
		result = 0
		for i in range(1, self.__numberOfInputs+1):
			result = result or self.getInputSignal(curIteration, "IN%i" % i).value
		self.appendToSignal(result)

	def getNumberOfInputs(self):
		"""
		Gets the total number of input ports.
		"""
		return self.__numberOfInputs


class AndBlock(BaseBlock):
	"""
	A simple block that will apply the :code:`and` operator to multiple inputs.
	This block expects and returns *falsy* and/or *truthy* values.

	Args:
		block_name (str):       The name of the block.
		numberOfInputs (int):   The amount of inputs. Defaults to 2.

	:Input Ports:
		- **IN1** -- The first input.
		- **IN2** -- The second input.
		- ...

	:Output Ports:
		**OUT1** -- Yields a 1 when all inputs are *truthy*. Otherwise, 0.
		In Python, 0 is a *falsy* value and can therefore be used as boolean check, or as computation
		value for other equation in the CBD. Similaryly, 1 is a *truthy* value.

	See Also:
		`Truthy and Falsy values in Python <https://docs.python.org/3/library/stdtypes.html#truth-value-testing>`_
	"""
	def __init__(self, block_name, numberOfInputs=2):
		BaseBlock.__init__(self, block_name, ["IN{0}".format(i) for i in range(1,numberOfInputs+1)], ["OUT1"])
		self.__numberOfInputs = numberOfInputs

	def	compute(self, curIteration):
		result = 1
		for i in range(1, self.__numberOfInputs+1):
			result = result and self.getInputSignal(curIteration, "IN"+str(i)).value
		self.appendToSignal(result)

	def getNumberOfInputs(self):
		"""
		Gets the total number of input ports.
		"""
		return self.__numberOfInputs


class DelayBlock(BaseBlock):
	"""
	A block that delays the input for one iteration.

	Args:
		block_name (str):       The name of the block.

	:Input Ports:
		- **IN1** -- The input.
		- **IC** -- The value to output at iteration 0 (i.e., the first iteration).

	:Output Ports:
		**OUT1** -- Outputs the input of the previous iteration.

	Note:
		The delay block is the only base block that alters the default behaviour
		of the dependency graph, because of the difference at iteration 0 and
		iteration 1.

	Warning:
		The block delays based on an iteration, not on a specific time-delay.
		When using adaptive stepsize simulation (either in the CBD simulator,
		or when exported), this block may be the cause for errors.

		For fixed step-size iterations, this block's behaviour is predictable,
		however, in adaptive stepsize, it may be more complicated. You may need
		to use the :class:`DeltaTBlock` for *frame-independent logic* (as it is
		called in the videogame-world) to ensure correct behaviour.

	See Also:
		`<https://drewcampbell92.medium.com/understanding-delta-time-b53bf4781a03>`_
	"""
	def __init__(self, block_name):
		BaseBlock.__init__(self, block_name, ["IN1", "IC"], ["OUT1"])

	def getDependencies(self, curIteration):
		# TO IMPLEMENT: This is a helper function you can use to create the dependency graph
		# Treat dependencies differently. For instance, at the first iteration (curIteration == 0), the block only depends on the IC;
		if curIteration == 0:
			return [self.getInputPortByName("IC").getIncoming().source]
		return []

	def compute(self, curIteration):
		if curIteration == 0:
			self.appendToSignal(self.getInputSignal(curIteration, "IC").value)
		else:
			self.appendToSignal(self.getInputSignal(curIteration - 1).value)


class DeltaTBlock(BaseBlock):
	"""
	Helperblock that will always output the current time delta, even when using
	adaptive step-size simulation.

	Args:
		block_name (str):   The name of the block.
		min (numeric):      The minimal value of the allowed delta T. Note that
							setting this argument will result in possibly invalid
							results. Defaults to 0.

	:Output Ports:
		**OUT1** -- The current time-delta.

	Note:
		Technically, this block is extraneous, as it re-uses information from
		the :class:`Clock`. However, it is meant to simplify the usage of time
		in CBD models. In general, this block is therefore preferred over the
		:code:`Clock` (unless you really know what you're doing).

	Warning:
		For fixed step-size iterations, you may need to use this block for
		*frame-independent logic* (as it is called in the videogame-world)
		to ensure correct behaviour.

	See Also:
		- :class:`TimeBlock`
		- :class:`Clock`
		- `<https://drewcampbell92.medium.com/understanding-delta-time-b53bf4781a03>`_
	"""
	def __init__(self, block_name, min=0.0):
		BaseBlock.__init__(self, block_name, [], ["OUT1"])
		self.min = min

	def getValue(self):
		"""Obtains the current time delta."""
		return self.getClock().getDeltaT()

	def compute(self, curIteration):
		self.appendToSignal(max(self.getValue(), self.min))


class TimeBlock(BaseBlock):
	"""
	Obtains the (current) absolute and relative time of the simulation.

	Args:
		block_name (str):   The name of the block.

	:Output Ports:
		- **OUT1** -- The absolute simulation time.
		- **relative** -- The relative current simulation time. If the simulation
		  started at a time :math:`t` :math:`(t > 0)`, this equals
		  :code:`OUT1` - :math:`t`.

	Note:
		Technically, this block is extraneous, as it re-uses information from
		the :class:`Clock`. However, it is meant to simplify the usage of time
		in CBD models. In general, this block is therefore preferred over the
		:code:`Clock` (unless you really know what you're doing).

	See Also:
		- :class:`DeltaTBlock`
		- :class:`Clock`
	"""
	def __init__(self, block_name):
		BaseBlock.__init__(self, block_name, [], ["OUT1", "relative"])

	def compute(self, curIteration):
		time = self.getClock().getTime(curIteration)
		rel_time = self.getClock().getRelativeTime(curIteration)
		self.appendToSignal(time)
		self.appendToSignal(rel_time, "relative")


import logging
class LoggingBlock(BaseBlock):
	"""
	A simple logging block that logs a string if the input is *truthy*.

	Args:
		block_name (str):   The name of the block.
		string (str):       The string to log.
		lev (int):          The level at which to log. Defaults to :data:`logging.WARNING`.
		logger (str):       The name of the logger. Defaults to :code:`CBDLogger`.

	:Input Ports:
		**IN1** -- The input.

	See Also:
		`Truthy and Falsy values in Python <https://docs.python.org/3/library/stdtypes.html#truth-value-testing>`_
	"""
	def __init__(self, block_name, string, lev=logging.WARNING, logger="CBD"):
		BaseBlock.__init__(self, block_name, ["IN1"], [])
		self.__string = string
		self.__logger = logging.getLogger(logger)
		self.__lev = lev

	def compute(self, curIteration):
		if self.getInputSignal(curIteration, "IN1").value:
			simtime = str(self.getClock().getTime(curIteration))
			if self.__lev == logging.WARNING:
				self.__logger.warning("[" + simtime + "]  " + self.__string, extra={"block": self})
			elif self.__lev == logging.ERROR:
				self.__logger.error("[" + simtime + "]  " + self.__string, extra={"block": self})
			elif self.__lev == logging.CRITICAL:
				self.__logger.critical("[" + simtime + "]  " + self.__string, extra={"block": self})


class AddOneBlock(CBD):
	"""
	Helperblock that adds 1 to the input. It is included as an example on how to
	create custom CBD blocks, while also really useful (it is used often for MUX).

	Args:
		block_name (str):   The name of the block.

	:Input Ports:
		**IN1** -- The input.

	:Output Ports:
		**OUT1** -- The input + 1.
	"""
	def __init__(self, block_name):
		CBD.__init__(self, block_name, ["IN1"], ["OUT1"])
		self.addBlock(ConstantBlock(block_name="OneConstant", value=1))
		self.addBlock(AdderBlock("PlusOne"))
		self.addConnection("IN1", "PlusOne")
		self.addConnection("OneConstant", "PlusOne")
		self.addConnection("PlusOne", "OUT1")


class DerivatorBlock(CBD):
	"""
	The derivator block is a CBD that calculates the derivative,
	using the backwards formula.

	.. versionchanged:: 1.4
		Replaced **delta_t** input port with internal :class:`DeltaTBlock`.

	Args:
		block_name (str):   The name of the block.

	:Input Ports:
		- **IN1** -- The input.
		- **IC** -- The initial condition. I.e., this value is outputted
		  at iteration 0.

	:Output Ports:
		**OUT1** -- The derivative of the input.
	"""
	def __init__(self, block_name):
		CBD.__init__(self, block_name, ["IN1", "IC"], ["OUT1"])
		self.addBlock(DeltaTBlock(block_name="delta_t", min=1e-6))
		self.addBlock(ProductBlock(block_name="multIc"))
		self.addBlock(NegatorBlock(block_name="neg1"))
		self.addBlock(AdderBlock(block_name="sum1"))
		self.addBlock(DelayBlock(block_name="delay"))
		self.addBlock(NegatorBlock(block_name="neg2"))
		self.addBlock(AdderBlock(block_name="sum2"))
		self.addBlock(ProductBlock(block_name="mult"))
		self.addBlock(InverterBlock(block_name="inv"))

		self.addConnection("IC", "multIc")
		self.addConnection("delta_t", "multIc")
		self.addConnection("multIc", "neg1")
		self.addConnection("neg1", "sum1")
		self.addConnection("IN1", "sum1")
		self.addConnection("sum1", "delay", input_port_name="IC")
		self.addConnection("IN1", "delay", input_port_name="IN1")
		self.addConnection("delay", "neg2")
		self.addConnection("neg2", "sum2")
		self.addConnection("IN1", "sum2")
		self.addConnection("sum2", "mult")
		self.addConnection("delta_t", "inv")
		self.addConnection("inv", "mult")
		self.addConnection("mult", "OUT1")


class IntegratorBlock(CBD):
	"""
	The integrator block is a CBD that calculates the integration.
	The block is implemented according to the backwards Euler rule.

	.. versionchanged:: 1.4
		Replaced **delta_t** input port with internal :class:`DeltaTBlock`.

	Args:
		block_name (str):   The name of the block.

	:Input Ports:
		- **IN1** -- The input.
		- **IC** -- The initial condition. I.e., this value is outputted
		  at iteration 0.

	:Output Ports:
		**OUT1** -- The integral of the input.
	"""
	def __init__(self, block_name):
		CBD.__init__(self, block_name, ["IN1", "IC"], ["OUT1"])
		self.addBlock(ConstantBlock(block_name="zero", value=0))
		self.addBlock(DeltaTBlock(block_name="delta_t"))
		self.addBlock(DelayBlock(block_name="delayIn"))
		self.addBlock(ProductBlock(block_name="multDelta"))
		self.addBlock(DelayBlock(block_name="delayState"))
		self.addBlock(AdderBlock(block_name="sumState"))

		self.addConnection("zero", "delayIn", input_port_name="IC")
		self.addConnection("IN1", "delayIn", input_port_name="IN1")
		self.addConnection("delayIn", "multDelta")
		self.addConnection("delta_t", "multDelta")
		self.addConnection("multDelta", "sumState")
		self.addConnection("IC", "delayState", input_port_name="IC")
		self.addConnection("delayState", "sumState")
		self.addConnection("sumState", "delayState", input_port_name="IN1")
		self.addConnection("sumState", "OUT1")


class Clock(BaseBlock):
	"""
	System clock. **Must be present in a simulation model.**

	Args:
		block_name (str):       The name of the block.
		start_delta (float):    Time delta at the start of the simulation. Defaults to 0.1.
		start_time (float):     Time at which the simulation starts. Defaults to 0.

	:Input Ports:
		**h** -- The delta for the next iteration. I.e., the time to wait until the next
				 iteration can be computed.

	:Output Ports:
		- **time** -- The current simulation time.
		- **rel_time** -- The relative simulation time, ignoring the start time.
		- **delta_t** -- The current delta.

	Warning:
		**Clock Usage Assumption:** When adding a (custom) clock to your model(s),
		its outputs will always represent the (relative) simulated time and time-delta,
		independent of the simulation algorithm used. I.e., changing the delay of a
		fixed-rate clock should only influence the accuracy of the signals, **not**
		the correctness of the signals. It is forbidden to misuse these outputs for
		specific simulations (e.g., using the :code:`time` as a counter, assuming
		:code:`delta_t` is a constant value...).

		In other words, the clock is guaranteed to output a correct value and should
		only be used in the context of "time". When exporting the CBD model to other
		formalisms/simulators, the Clock's outputs should be replaced with the
		corresponding simulator's clock without loss of generality.

	See Also:
		- :class:`TimeBlock`
		- :class:`DeltaTBlock`
	"""
	def __init__(self, block_name, start_delta=0.1, start_time=0.0):
		BaseBlock.__init__(self, block_name, ["h"], ["time", "rel_time", "delta_t"])
		self.__start_delta = start_delta
		self.__start_time = start_time
		self.__delta = self.__start_delta
		self.__time = self.__start_time

	def getDependencies(self, curIteration):
		return []

	def compute(self, curIteration):
		self.appendToSignal(self.__time, "time")
		self.appendToSignal(self.getRelativeTime(curIteration), "rel_time")
		self.appendToSignal(self.__delta, "delta_t")

		if curIteration > 0:
			self.__delta = self.getInputSignal(curIteration - 1, "h").value
		self.__time += self.__delta

	def getStartTime(self):
		"""
		Gets the starting time of the model.
		"""
		return self.__start_time

	def getTime(self, curIt):
		"""
		Gets the time of the clock at a certain iteration.

		Args:
			curIt (int):    The iteration to look at.
		"""
		thist = self.getSignalHistory("time")
		if len(thist) == 0:
			return self.__start_time
		if len(thist) <= curIt:
			return thist[-1][1] + self.__delta
		return thist[curIt][1]

	def getRelativeTime(self, curIt):
		"""
		Gets the relative simulation time (ignoring the start time).

		Args:
			curIt (int):    The iteration to look at.
		"""
		return self.getTime(curIt) - self.__start_time

	def setStartTime(self, start_time=0.0):
		self.__start_time = start_time

	def setDeltaT(self, delta_t=0.1):
		self.__delta = delta_t

	def getDeltaT(self):
		return self.__delta

	def reset(self):
		"""
		Resets the clock. Required for restarting a simulation.
		"""
		self.clearPorts()
		self.__time = self.__start_time
		self.__delta = self.__start_delta

	def _rewind(self):
		self.__time -= self.__delta
		BaseBlock._rewind(self)
		self.__delta = self.getInputSignal(-1, "h").value


class SequenceBlock(BaseBlock):
	"""
	A simple sequence block. Will output the sequence iteratively.

	Args:
		block_name (str):   The name of the block.
		sequence (iter):    The sequence that needs to be outputted.

	:Output Ports:
		**OUT1** -- The values from the sequence.

	Warning:
		Preferably only use this block in the tests!
	"""
	def __init__(self, block_name, sequence):
		BaseBlock.__init__(self, block_name, [], ["OUT1"])
		self.__sequence = sequence

	def compute(self, curIteration):
		self.appendToSignal(self.__sequence[curIteration % len(self.__sequence)])
