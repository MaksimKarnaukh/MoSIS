#!/usr/bin/env python
"""
Unittest for the basic CBD features
"""

import unittest

from pyCBD.Core import *
from pyCBD.lib.std import *
from pyCBD.simulator import Simulator

NUM_DISCR_TIME_STEPS = 5

class BasicCBDTestCase(unittest.TestCase):
	def setUp(self):
		self.CBD = CBD("CBD_for_block_under_test")
		self.sim = Simulator(self.CBD)

	def _run(self, num_steps=1, delta_t = 1.0):
		self.sim.setDeltaT(delta_t)
		self.sim.setTerminationTime(num_steps * delta_t)
		self.CBD.addFixedRateClock("clock", delta_t, )
		self.sim.run()

	def _getSignal(self, blockname, output_port = None):
		block = self.CBD.getBlockByName(blockname)
		signal =  block.getSignalHistory(name_output = output_port)
		return [x.value for x in signal]

	def testLinearStrongComponent(self):
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=5.5))
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=-5))
		self.CBD.addBlock(AdderBlock(block_name="a1"))
		self.CBD.addBlock(AdderBlock(block_name="a3"))
		self.CBD.addBlock(AdderBlock(block_name="a2"))

		self.CBD.addConnection("a3", "a1")
		self.CBD.addConnection("c1", "a1")
		self.CBD.addConnection("a1", "a3")
		self.CBD.addConnection("a2", "a3")
		self.CBD.addConnection("c2", "a2")
		self.CBD.addConnection("a3", "a2")
		self._run(NUM_DISCR_TIME_STEPS)
		self.assertEqual(self._getSignal("a1"), [-5.5]*5)
		self.assertEqual(self._getSignal("a2"), [5.0]*5)
		self.assertEqual(self._getSignal("a3"), [-0.5]*5)

	def testLinearStrongComponentWithDelay(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=3.0))
		self.CBD.addBlock(AdderBlock(block_name="sum"))
		self.CBD.addBlock(DelayBlock(block_name="delay"))
		self.CBD.addBlock(NegatorBlock(block_name="neg"))

		self.CBD.addConnection("c1", "sum")
		self.CBD.addConnection("neg", "sum")
		self.CBD.addConnection("sum", "delay", input_port_name="IC")
		self.CBD.addConnection("delay", "neg")
		self.CBD.addConnection("neg", "delay")

		self._run(1)
		self.assertEqual(self._getSignal("delay"), [1.5])

	def testLinearStrongComponentWithMult(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=3))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=5))
		self.CBD.addBlock(AdderBlock(block_name="a"))
		self.CBD.addBlock(ProductBlock(block_name="p"))

		self.CBD.addConnection("c1", "a")
		self.CBD.addConnection("p", "a")
		self.CBD.addConnection("a", "p")
		self.CBD.addConnection("c2", "p")
		self._run(NUM_DISCR_TIME_STEPS)
		self.assertEqual(self._getSignal("a"), [-0.75]*5)
		self.assertEqual(self._getSignal("p"), [-3.75]*5)

	def testLinearStrongComponentWithNeg(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=5))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=8))
		self.CBD.addBlock(AdderBlock(block_name="a1"))
		self.CBD.addBlock(AdderBlock(block_name="a2"))
		self.CBD.addBlock(NegatorBlock(block_name="n"))

		self.CBD.addConnection("c1", "a1")
		self.CBD.addConnection("a2", "a1")
		self.CBD.addConnection("c2", "a2")
		self.CBD.addConnection("n", "a2")
		self.CBD.addConnection("a1", "n")
		self._run(NUM_DISCR_TIME_STEPS)
		self.assertEqual(self._getSignal("a1"), [6.5]*5)
		self.assertEqual(self._getSignal("a2"), [1.5]*5)
		self.assertEqual(self._getSignal("n"), [-6.5]*5)

	def testLinearStrongComponentWithGen(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=4))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=2))
		self.CBD.addBlock(AdderBlock(block_name="a1"))
		self.CBD.addBlock(AdderBlock(block_name="a2"))
		self.CBD.addBlock(GenericBlock(block_name="s", block_operator="sqrt"))

		self.CBD.addConnection("c1", "a1")
		self.CBD.addConnection("a2", "a1")
		self.CBD.addConnection("c2", "a2")
		self.CBD.addConnection("s", "a2")
		self.CBD.addConnection("a1", "s")
		self.assertRaises(SystemExit, self._run, NUM_DISCR_TIME_STEPS)

	def testTwoLinearStrongComponent(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=3))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=2))
		self.CBD.addBlock(ConstantBlock(block_name="c3", value=1.5))
		self.CBD.addBlock(ConstantBlock(block_name="c4", value=1))
		self.CBD.addBlock(AdderBlock(block_name="a1"))
		self.CBD.addBlock(AdderBlock(block_name="a2"))
		self.CBD.addBlock(AdderBlock(block_name="a3"))
		self.CBD.addBlock(AdderBlock(block_name="a4"))
		self.CBD.addBlock(AdderBlock(block_name="a5"))
		self.CBD.addBlock(ProductBlock(block_name="p"))
		self.CBD.addBlock(NegatorBlock(block_name="n1"))
		self.CBD.addBlock(NegatorBlock(block_name="n2"))

		self.CBD.addConnection("a3", "a1")
		self.CBD.addConnection("c1", "a1")
		self.CBD.addConnection("c2", "a2")
		self.CBD.addConnection("a3", "a2")
		self.CBD.addConnection("a1", "a3")
		self.CBD.addConnection("a2", "a3")
		self.CBD.addConnection("a3", "p")
		self.CBD.addConnection("c3", "p")
		self.CBD.addConnection("p", "n1")
		self.CBD.addConnection("n1", "a4")
		self.CBD.addConnection("a5", "a4")
		self.CBD.addConnection("c4", "a5")
		self.CBD.addConnection("n2", "a5")
		self.CBD.addConnection("a4", "n2")
		self._run(NUM_DISCR_TIME_STEPS)
		self.assertEqual(self._getSignal("a1"), [-2.0]*5)
		self.assertEqual(self._getSignal("a2"), [-3.0]*5)
		self.assertEqual(self._getSignal("a3"), [-5.0]*5)
		self.assertEqual(self._getSignal("a4"), [4.25]*5)
		self.assertEqual(self._getSignal("a5"), [-3.25]*5)
		self.assertEqual(self._getSignal("p"), [-7.5]*5)
		self.assertEqual(self._getSignal("n1"), [7.5]*5)
		self.assertEqual(self._getSignal("n2"), [-4.25]*5)

	def testNonLinearStrongComponent(self):
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=15))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=10))
		self.CBD.addBlock(AdderBlock(block_name="a1"))
		self.CBD.addBlock(AdderBlock(block_name="a2"))
		self.CBD.addBlock(ProductBlock(block_name="p"))

		self.CBD.addConnection("c2", "a1")
		self.CBD.addConnection("p", "a1")
		self.CBD.addConnection("a1", "p")
		self.CBD.addConnection("a2", "p")
		self.CBD.addConnection("p", "a2")
		self.CBD.addConnection("c1", "a2")
		self.assertRaises(SystemExit, self._run, NUM_DISCR_TIME_STEPS)

if __name__ == '__main__':  # pragma: no cover
	# When this module is executed from the command-line, run all its tests
	unittest.main(verbosity=2)

  
  
  
  
  
  
  
  
