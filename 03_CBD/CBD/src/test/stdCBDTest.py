#!/usr/bin/env python
"""
Unit tests for all the basic CBD blocks in the std library.
"""

import unittest

from pyCBD.Core import *
from pyCBD.lib.std import *
from pyCBD.simulator import Simulator

NUM_DISCR_TIME_STEPS = 5

class StdCBDTestCase(unittest.TestCase):
	def setUp(self):
		self.CBD = CBD("CBD_for_block_under_test")
		self.sim = Simulator(self.CBD)

	def _run(self, num_steps=1, delta_t = 1.0):
		self.sim.setDeltaT(delta_t)
		self.sim.setTerminationTime(num_steps * delta_t)
		self.CBD.addFixedRateClock("clock", delta_t)
		self.sim.run()

	def _getSignal(self, blockname, output_port = None):
		block = self.CBD.getBlockByName(blockname)
		signal =  block.getSignalHistory(name_output = output_port)
		return [x.value for x in signal]

	def testConstantBlock(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=3.3))

		self._run(NUM_DISCR_TIME_STEPS)
		self.assertEqual(self._getSignal("c1"), [3.3] * NUM_DISCR_TIME_STEPS)

		self.CBD.getBlockByName("c1").setValue(5)
		self.assertEqual(self.CBD.getBlockByName("c1").getValue(), 5)

	def testNegatorBlockPos(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=6.0))
		self.CBD.addBlock(NegatorBlock(block_name="n"))
		self.CBD.addConnection("c1", "n")

		self._run(NUM_DISCR_TIME_STEPS)
		self.assertEqual(self._getSignal("n"), [-6.0] * NUM_DISCR_TIME_STEPS)

	def testNegatorBlockNeg(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=-6.0))
		self.CBD.addBlock(NegatorBlock(block_name="n"))
		self.CBD.addConnection("c1", "n")

		self._run(NUM_DISCR_TIME_STEPS)
		self.assertEqual(self._getSignal("n"), [6.0] * NUM_DISCR_TIME_STEPS)

	def testNegatorBlockZero(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=0.0))
		self.CBD.addBlock(NegatorBlock(block_name="n"))
		self.CBD.addConnection("c1", "n")

		self._run(NUM_DISCR_TIME_STEPS)
		self.assertEqual(self._getSignal("n"), [0.0] * NUM_DISCR_TIME_STEPS)

	def testInverterBlock(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=5.0))
		self.CBD.addBlock(InverterBlock(block_name="i1"))
		self.CBD.addBlock(InverterBlock(block_name="i2"))

		self.CBD.addConnection("c1", "i1")
		self.CBD.addConnection("i1", "i2")
		self._run(NUM_DISCR_TIME_STEPS)
		self.assertEqual(self._getSignal("i1"), [0.2] * NUM_DISCR_TIME_STEPS)
		self.assertEqual(self._getSignal("i2"), [5.0] * NUM_DISCR_TIME_STEPS)

	def testInverterBlockDivByZero(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=0))
		self.CBD.addBlock(InverterBlock(block_name="inv"))

		self.CBD.addConnection("c1", "inv")
		self.assertRaises(ZeroDivisionError, self._run, NUM_DISCR_TIME_STEPS)

	def testAdderBlock(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=2.0))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=6.0))
		self.CBD.addBlock(AdderBlock(block_name="a"))

		self.CBD.addConnection("c1", "a")
		self.CBD.addConnection("c2", "a")
		self._run(NUM_DISCR_TIME_STEPS)
		self.assertEqual(self._getSignal("a"), [8.0] * NUM_DISCR_TIME_STEPS)

	def testAdderBlock2(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=2.0))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=-6.0))
		self.CBD.addBlock(AdderBlock(block_name="a", numberOfInputs=5))

		self.assertEqual(self.CBD.getBlockByName("a").getNumberOfInputs(), 5)

		self.CBD.addConnection("c1", "a")
		self.CBD.addConnection("c2", "a")
		self.CBD.addConnection("c1", "a")
		self.CBD.addConnection("c2", "a")
		self.CBD.addConnection("c1", "a")
		self._run(NUM_DISCR_TIME_STEPS)
		self.assertEqual(self._getSignal("a"), [-6.0] * NUM_DISCR_TIME_STEPS)

	def testProductBlock(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=2.0))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=5.0))
		self.CBD.addBlock(ProductBlock(block_name="p"))

		self.CBD.addConnection("c1", "p")
		self.CBD.addConnection("c2", "p")
		self._run(NUM_DISCR_TIME_STEPS)
		self.assertEqual(self._getSignal("p"), [10.0] * 5)

	def testProductBlock2(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=0.5))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=4.0))
		self.CBD.addBlock(ProductBlock(block_name="p", numberOfInputs=4))

		self.assertEqual(self.CBD.getBlockByName("p").getNumberOfInputs(), 4)

		self.CBD.addConnection("c1", "p")
		self.CBD.addConnection("c2", "p")
		self.CBD.addConnection("c1", "p")
		self.CBD.addConnection("c2", "p")
		self._run(NUM_DISCR_TIME_STEPS)
		self.assertEqual(self._getSignal("p"), [4.0] * 5)

	def testGenericBlock(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=2.2))
		self.CBD.addBlock(GenericBlock(block_name="g", block_operator="ceil"))

		self.CBD.addConnection("c1", "g")
		self._run(NUM_DISCR_TIME_STEPS)
		self.assertEqual(self._getSignal("g"), [3.0] * 5)

	def testRootBlock(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=8.0))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=3.0))
		self.CBD.addBlock(RootBlock(block_name="g"))

		self.CBD.addConnection("c1", "g", input_port_name="IN1")
		self.CBD.addConnection("c2", "g", input_port_name="IN2")
		self._run(1)
		self.assertEqual(self._getSignal("g"), [2.0])

	def testRootBlock2(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=9.0))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=2.0))
		self.CBD.addBlock(RootBlock(block_name="g"))

		self.CBD.addConnection("c1", "g", input_port_name="IN1")
		self.CBD.addConnection("c2", "g", input_port_name="IN2")
		self._run(1)
		self.assertEqual(self._getSignal("g"), [3.0])

	def testRootBlockDivByZero(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=0))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=2.0))
		self.CBD.addBlock(RootBlock(block_name="root"))

		self.CBD.addConnection("c2", "root", input_port_name="IN1")
		self.CBD.addConnection("c1", "root", input_port_name="IN2")
		self.assertRaises(ZeroDivisionError, self._run, NUM_DISCR_TIME_STEPS)

	def testPowerBlock(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=8.0))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=3.0))
		self.CBD.addBlock(PowerBlock(block_name="g"))

		self.CBD.addConnection("c1", "g", input_port_name="IN1")
		self.CBD.addConnection("c2", "g", input_port_name="IN2")
		self._run(1)
		self.assertEqual(self._getSignal("g"), [512.0])

	def testAbsBlock(self):
		seq = [1, -1, 2, -6, -9, 7]
		self.CBD.addBlock(SequenceBlock(block_name="seq", sequence=seq))
		self.CBD.addBlock(AbsBlock(block_name="abs"))

		self.CBD.addConnection("seq", "abs")
		self._run(len(seq))
		self.assertEqual(self._getSignal("abs"), [abs(x) for x in seq])

	def testMaxBlock(self):
		self.CBD.addBlock(TimeBlock("time"))
		self.CBD.addBlock(ConstantBlock("c1", -2))
		self.CBD.addBlock(ConstantBlock("c2", 3.0))
		self.CBD.addBlock(AdderBlock("sum"))

		self.CBD.addBlock(MaxBlock(block_name="max", numberOfInputs=3))

		self.assertEqual(self.CBD.getBlockByName("max").getNumberOfInputs(), 3)

		self.CBD.addConnection("time", "sum")
		self.CBD.addConnection("c1", "sum")
		self.CBD.addConnection("sum", "max")
		self.CBD.addConnection("c2", "max")
		self.CBD.addConnection("time", "max")
		self._run(5)
		self.assertEqual(self._getSignal("max"), [max(float(x), 3.0, x + 2.0) for x in range(-2, 3)])

	def testMinBlock(self):
		self.CBD.addBlock(TimeBlock("time"))
		self.CBD.addBlock(ConstantBlock("c1", -2))
		self.CBD.addBlock(ConstantBlock("c2", 3.0))
		self.CBD.addBlock(AdderBlock("sum"))

		self.CBD.addBlock(MinBlock(block_name="min", numberOfInputs=3))

		self.assertEqual(self.CBD.getBlockByName("min").getNumberOfInputs(), 3)

		self.CBD.addConnection("time", "sum")
		self.CBD.addConnection("c1", "sum")
		self.CBD.addConnection("sum", "min")
		self.CBD.addConnection("c2", "min")
		self.CBD.addConnection("time", "min")
		self._run(5)
		self.assertEqual(self._getSignal("min"), [min(float(x), 3.0, x + 2.0) for x in range(-2, 3)])

	def testClampBlock(self):
		self.CBD.addBlock(TimeBlock("time"))
		self.CBD.addBlock(ConstantBlock("c1", -2))
		self.CBD.addBlock(AdderBlock("sum"))

		self.CBD.addBlock(ClampBlock(block_name="clamp", min=-1.0, max=2.0))

		self.CBD.addConnection("time", "sum")
		self.CBD.addConnection("c1", "sum")
		self.CBD.addConnection("sum", "clamp")
		self._run(5)
		self.assertEqual(self._getSignal("clamp"), [max(min(float(x), 2.0), -1.0) for x in range(-2, 3)])

	def testClampBlock2(self):
		self.CBD.addBlock(TimeBlock("time"))
		self.CBD.addBlock(ConstantBlock("c1", -2))
		self.CBD.addBlock(ConstantBlock("c2", -1.0))
		self.CBD.addBlock(ConstantBlock("c3", 2.0))
		self.CBD.addBlock(AdderBlock("sum"))

		self.CBD.addBlock(ClampBlock(block_name="clamp", use_const=False))

		self.CBD.addConnection("time", "sum")
		self.CBD.addConnection("c1", "sum")
		self.CBD.addConnection("sum", "clamp", input_port_name="IN1")
		self.CBD.addConnection("c2", "clamp", input_port_name="IN2")
		self.CBD.addConnection("c3", "clamp", input_port_name="IN3")
		self._run(5)
		self.assertEqual(self._getSignal("clamp"), [max(min(float(x), 2.0), -1.0) for x in range(-2, 3)])

	def testMultiplexerBlock(self):
		a = list(range(10))
		b = list(range(100, 90, -1))
		s = [0, 1, 1, 0, 0, 0, 1, 1, 1, 0]
		self.CBD.addBlock(SequenceBlock(block_name="c1", sequence=a))
		self.CBD.addBlock(SequenceBlock(block_name="c2", sequence=b))
		self.CBD.addBlock(SequenceBlock(block_name="c3", sequence=s))
		self.CBD.addBlock(MultiplexerBlock(block_name="mux"))

		self.CBD.addConnection("c1", "mux", input_port_name="IN1")
		self.CBD.addConnection("c2", "mux", input_port_name="IN2")
		self.CBD.addConnection("c3", "mux", input_port_name="select")
		self._run(10)
		self.assertEqual(self._getSignal("mux"), [0, 99, 98, 3, 4, 5, 94, 93, 92, 9])

	def testIntBlock(self):
		seq = [1.2, 2.2, 3.8, 4.7, 2.3, 6.6666]
		self.CBD.addBlock(SequenceBlock(block_name="seq", sequence=seq))
		self.CBD.addBlock(IntBlock(block_name="int"))

		self.CBD.addConnection("seq", "int")
		self._run(len(seq))
		self.assertEqual(self._getSignal("int"), [int(x) for x in seq])

	def testLessThanBlock1(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=2))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=6))
		self.CBD.addBlock(LessThanBlock(block_name="lt"))

		self.CBD.addConnection("c1", "lt", input_port_name="IN1")
		self.CBD.addConnection("c2", "lt", input_port_name="IN2")
		self._run(1)
		self.assertEqual(self._getSignal("lt"), [1])

	def testLessThanBlock2(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=9))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=7))
		self.CBD.addBlock(LessThanBlock(block_name="lt"))

		self.CBD.addConnection("c1", "lt", input_port_name="IN1")
		self.CBD.addConnection("c2", "lt", input_port_name="IN2")
		self._run(1)
		self.assertEqual(self._getSignal("lt"), [0])

	def testLessThanBlock3(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=5))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=5))
		self.CBD.addBlock(LessThanBlock(block_name="lt"))

		self.CBD.addConnection("c1", "lt", input_port_name="IN1")
		self.CBD.addConnection("c2", "lt", input_port_name="IN2")
		self._run(1)
		self.assertEqual(self._getSignal("lt"), [0])

	def testLessThanOrEqualsBlock1(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=2))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=6))
		self.CBD.addBlock(LessThanOrEqualsBlock(block_name="leq"))

		self.CBD.addConnection("c1", "leq", input_port_name="IN1")
		self.CBD.addConnection("c2", "leq", input_port_name="IN2")
		self._run(1)
		self.assertEqual(self._getSignal("leq"), [1])

	def testLessThanOrEqualsBlock2(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=9))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=7))
		self.CBD.addBlock(LessThanOrEqualsBlock(block_name="leq"))

		self.CBD.addConnection("c1", "leq", input_port_name="IN1")
		self.CBD.addConnection("c2", "leq", input_port_name="IN2")
		self._run(1)
		self.assertEqual(self._getSignal("leq"), [0])

	def testLessThanOrEqualsBlock3(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=5))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=5))
		self.CBD.addBlock(LessThanOrEqualsBlock(block_name="leq"))

		self.CBD.addConnection("c1", "leq", input_port_name="IN1")
		self.CBD.addConnection("c2", "leq", input_port_name="IN2")
		self._run(1)
		self.assertEqual(self._getSignal("leq"), [1])

	def testEqualsBlock1(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=5))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=5))
		self.CBD.addBlock(EqualsBlock(block_name="eq"))

		self.CBD.addConnection("c1", "eq")
		self.CBD.addConnection("c2", "eq")
		self._run(1)
		self.assertEqual(self._getSignal("eq"), [1])

	def testEqualsBlock2(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=4))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=7))
		self.CBD.addBlock(EqualsBlock(block_name="eq"))

		self.CBD.addConnection("c1", "eq")
		self.CBD.addConnection("c2", "eq")
		self._run(1)
		self.assertEqual(self._getSignal("eq"), [0])

	def testNotBlock1(self):
		self.CBD.addBlock(ConstantBlock(block_name="c", value=0))
		self.CBD.addBlock(NotBlock(block_name="not"))

		self.CBD.addConnection("c", "not")
		self._run(1)
		self.assertEqual(self._getSignal("not"), [1])

	def testNotBlock2(self):
		self.CBD.addBlock(ConstantBlock(block_name="c", value=1))
		self.CBD.addBlock(NotBlock(block_name="not"))

		self.CBD.addConnection("c", "not")
		self._run(1)
		self.assertEqual(self._getSignal("not"), [0])

	def testNotBlock3(self):
		self.CBD.addBlock(ConstantBlock(block_name="c", value=17))
		self.CBD.addBlock(NotBlock(block_name="not"))

		self.CBD.addConnection("c", "not")
		self._run(1)
		self.assertEqual(self._getSignal("not"), [0])

	def testAndBlock(self):
		self.CBD.addBlock(SequenceBlock(block_name="c1", sequence=[0, 0, 1, 1]))
		self.CBD.addBlock(SequenceBlock(block_name="c2", sequence=[0, 1, 0, 1]))
		self.CBD.addBlock(AndBlock(block_name="and"))

		self.CBD.addConnection("c1", "and")
		self.CBD.addConnection("c2", "and")
		self._run(4)
		self.assertEqual(self._getSignal("and"), [0, 0, 0, 1])

	def testOrBlock(self):
		self.CBD.addBlock(SequenceBlock(block_name="c1", sequence=[0, 0, 1, 1]))
		self.CBD.addBlock(SequenceBlock(block_name="c2", sequence=[0, 1, 0, 1]))
		self.CBD.addBlock(OrBlock(block_name="or"))

		self.CBD.addConnection("c1", "or")
		self.CBD.addConnection("c2", "or")
		self._run(4)
		self.assertEqual(self._getSignal("or"), [0, 1, 1, 1])

	def testModuloBlock(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=8.0))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=3.0))
		self.CBD.addBlock(ModuloBlock(block_name="g"))

		self.CBD.addConnection("c1", "g", input_port_name="IN1")
		self.CBD.addConnection("c2", "g", input_port_name="IN2")
		self._run(1)
		self.assertEqual(self._getSignal("g"), [2.0])

	def testModuloBlock2(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=8.0))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=8.0))
		self.CBD.addBlock(ModuloBlock(block_name="g"))

		self.CBD.addConnection("c1", "g", input_port_name="IN1")
		self.CBD.addConnection("c2", "g", input_port_name="IN2")
		self._run(1)
		self.assertEqual(self._getSignal("g"), [0.0])

	def testPreviousValueDelayBlock(self):
		self.CBD.addBlock(ConstantBlock(block_name="ZeroConstant", value=0.0))
		self.CBD.addBlock(SequenceBlock(block_name="seq", sequence=[0, 2, 4, 6, 8, 10, 12]))
		self.CBD.addBlock(DelayBlock(block_name="d"))

		self.CBD.addConnection("ZeroConstant", "d", input_port_name="IC")
		self.CBD.addConnection("seq", "d")

		self._run(7, 0.5)
		self.assertEqual(self._getSignal("d"), [0, 0, 2, 4, 6, 8, 10])

	def testPreviousValueDelayBlock2(self):
		self.CBD.addBlock(SequenceBlock(block_name="FirstSeq", sequence=[2, 12, 22, 23, 32, 11, 91]))
		self.CBD.addBlock(SequenceBlock(block_name="SecSeq", sequence=[5, 5, 5, 5, 3, 3, 3]))
		self.CBD.addBlock(DelayBlock(block_name="prev"))
		self.CBD.addConnection(self.CBD.getBlockByName("FirstSeq"), "prev")
		self.CBD.addConnection(self.CBD.getBlockByName("SecSeq"), "prev", input_port_name="IC")
		self._run(7)
		self.assertEqual(self._getSignal("prev"), [5, 2, 12, 22, 23, 32, 11])

	def testSequenceBlock(self):
		self.CBD.addBlock(SequenceBlock(block_name="FirstSeq", sequence=[2, 2, 2, 3, 2, 1, 1]))
		self._run(7)
		self.assertEqual(self._getSignal("FirstSeq"), [2, 2, 2, 3, 2, 1, 1])

	def testLoggingBlockError(self):
		self.CBD.addBlock(ConstantBlock(block_name="One", value=1))
		self.CBD.addBlock(LoggingBlock("L1", "Logging block test were level is error", logging.ERROR))
		self.CBD.addConnection("One", "L1")
		self.assertRaises(SystemExit, self._run, 1)

	def testLoggingBlockWarning(self):
		self.CBD.addBlock(ConstantBlock(block_name="One", value=1))
		self.CBD.addBlock(LoggingBlock("L1", "Logging block test were level is warning", logging.WARNING))
		self.CBD.addConnection("One", "L1")
		self._run(1)

	def testLoggingBlockFatal(self):
		self.CBD.addBlock(ConstantBlock(block_name="One", value=1))
		self.CBD.addBlock(LoggingBlock("L1", "Logging block test were level is fatal", logging.CRITICAL))
		self.CBD.addConnection("One", "L1")
		self.assertRaises(SystemExit, self._run, 1)

	def initializeFuncDerBas(self):
		#f(t) = 5*t
		CBDFunc = CBD("function", output_ports = ["OUT1"])
		CBDFunc.addBlock(TimeBlock(block_name="t"))
		CBDFunc.addBlock(ProductBlock(block_name="p"))
		CBDFunc.addBlock(ConstantBlock(block_name="c", value=5.0))
		CBDFunc.addConnection("t", "p")
		CBDFunc.addConnection("c", "p")
		CBDFunc.addConnection("p", "OUT1")
		return CBDFunc

	def testDerivatorBlock(self):
		self.CBD.addBlock(ConstantBlock(block_name="zero", value=0.0))
		CBDFunc = self.initializeFuncDerBas()
		self.CBD.addBlock(CBDFunc)
		self.CBD.addBlock(DerivatorBlock(block_name="der"))

		self.CBD.addConnection("zero", "der", input_port_name="IC")
		self.CBD.addConnection("function", "der")
		self._run(5)
		self.assertEqual(self._getSignal("der"), [0.0]+[5.0]*4)

	def testIntegratorBlock(self):
		# Function: f(t) = 6 + f(t - dt), where f(0) = 6
		dt = 0.0001
		epsilon = 0.002
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=6.0))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=0.0))
		self.CBD.addBlock(AdderBlock(block_name="a"))
		self.CBD.addBlock(DelayBlock(block_name="d"))

		self.CBD.addBlock(IntegratorBlock(block_name="int"))
		self.CBD.addConnection("a", "int")
		self.CBD.addConnection("c2", "int", input_port_name="IC")

		self.CBD.addConnection("c1", "a")
		self.CBD.addConnection("d", "a")
		self.CBD.addConnection("a", "d")
		self.CBD.addConnection("c2", "d", input_port_name="IC")
		self._run(NUM_DISCR_TIME_STEPS, dt)
		actual = [x*dt for x in [0.0, 9.0, 24.0, 45.0, 72.0]]
		measured = self._getSignal("int")
		error = [abs(measured[i] - actual[i]) for i in range(NUM_DISCR_TIME_STEPS)]
		self.assertFalse(any([x > epsilon for x in error]), "Error too large.\n\tExpected: {}\n\tActual: {}"
		                                                    "\n\tErrors: {}".format(actual, measured, error))

	def testDelayBlock(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=5.0))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=3.0))
		self.CBD.addBlock(DelayBlock(block_name="d"))

		self.CBD.addConnection("c2", "d")
		self.CBD.addConnection("c1", "d", input_port_name="IC")
		self._run(4)
		self.assertEqual(self._getSignal("d"), [5.0, 3.0, 3.0, 3.0])

	def testDelayBlock2(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=1.0))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=5.0))
		self.CBD.addBlock(DelayBlock(block_name="d"))
		self.CBD.addBlock(AdderBlock(block_name="a"))

		self.CBD.addConnection("c2", "a")
		self.CBD.addConnection("d", "a")
		self.CBD.addConnection("c1", "d", input_port_name="IC")
		self.CBD.addConnection("a", "d")
		self._run(5)
		self.assertEqual(self._getSignal("d"), [1.0, 6.0, 11.0, 16.0, 21.0])

	def testAddOneBlock(self):
		self.CBD.addBlock(SequenceBlock(block_name="c", sequence=[1, 2, 5, 7, 3]))
		self.CBD.addBlock(AddOneBlock(block_name="add1"))

		self.CBD.addConnection("c", "add1")
		self._run(5)
		self.assertEqual(self._getSignal("add1"), [2, 3, 6, 8, 4])

if __name__ == '__main__':  # pragma: no cover
	# When this module is executed from the command-line, run all its tests
	unittest.main(verbosity=2)

  
  
  
  
  
  
  
  
