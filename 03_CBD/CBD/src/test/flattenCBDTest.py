#!/usr/bin/env python
#
# Unit tests for the flatten function on the CBD

import unittest
from pyCBD.Core import *
from pyCBD.lib.std import *
from pyCBD.simulator import Simulator

class FlattenCBDTest(unittest.TestCase):
	def setUp(self):
		self.CBD = CBD("block_under_test")
		self.sim = Simulator(self.CBD)
		
	def _run(self, num_steps=1, step = 1):
		self.sim.setDeltaT(step)
		self.sim.setTerminationTime(num_steps * step)
		self.sim.run()

	def _getSignal(self, blockname, output_port = None):
		if blockname == "":
			block = self.CBD
		else:
			block = self.CBD.getBlockByName(blockname)
		signal =  block.getSignalHistory(name_output = output_port)
		return [x.value for x in signal]

	def testFlatten(self):
		self.CBD.addOutputPort("OUT1")
		self.CBD.addBlock(AddOneBlock(block_name="add1"))
		self.CBD.addBlock(TimeBlock("time"))
		self.CBD.addConnection("time", "add1")
		self.CBD.addConnection("add1", "OUT1")
		self.CBD.flatten()

		self.assertEqual(set([x.getBlockName() for x in self.CBD.getBlocks()]),
		                 {'time', 'add1.OneConstant', 'add1.PlusOne'})

		self._run(5)

		self.assertEqual([s.value for s in self.CBD.getSignalHistory("OUT1")], [1., 2., 3., 4., 5.])
							
	def testInterCBD(self):
		CBDLittle1 = CBD("first_child", output_ports = ["outCBD1"])
		CBDLittle2 = CBD("second_child", input_ports = ["inCBD2"])
		
		self.CBD.addBlock(CBDLittle1)
		self.CBD.addBlock(CBDLittle2)
		self.CBD.addConnection("first_child", "second_child", input_port_name="inCBD2", output_port_name="outCBD1")

		CBDLittle1.addBlock(ConstantBlock(block_name="c1", value=2.0))
		CBDLittle1.addConnection("c1", "outCBD1")
		
		self.CBD.flatten()
		self._run(5)
		self.assertEqual(self._getSignal("first_child.c1"), [2.0]*5)

		
	def testLinearStrongComponentWithMult(self):
		CBDConstant1 = CBD("constantCBD1", output_ports = ["outConstant1"])
		CBDConstant1.addBlock(ConstantBlock(block_name="c", value=3))
		CBDConstant1.addConnection("c", "outConstant1")
		
		CBDConstant2 = CBD("constantCBD2", output_ports = ["outConstant2"])
		CBDConstant2.addBlock(ConstantBlock(block_name="c", value=5))
		CBDConstant2.addConnection("c", "outConstant2")
		
		CBDAdder = CBD("adderCBD", input_ports = ["in1Add", "in2Add"], output_ports = ["outAdd"])
		CBDAdder.addBlock(AdderBlock(block_name="a"))
		CBDAdder.addConnection("in1Add", "a")
		CBDAdder.addConnection("in2Add", "a")
		CBDAdder.addConnection("a", "outAdd")
		
		CBDProduct = CBD("productCBD", input_ports = ["in1Prod", "in2Prod"], output_ports = ["outProd"])
		CBDProduct.addBlock(ProductBlock(block_name="p"))
		CBDProduct.addConnection("in1Prod", "p")
		CBDProduct.addConnection("in2Prod", "p")
		CBDProduct.addConnection("p", "outProd")
		
		self.CBD.addBlock(CBDConstant1)
		self.CBD.addBlock(CBDConstant2)
		self.CBD.addBlock(CBDAdder)
		self.CBD.addBlock(CBDProduct)
		self.CBD.addConnection("constantCBD1", "adderCBD", input_port_name="in1Add", output_port_name="outConstant1")
		self.CBD.addConnection("productCBD", "adderCBD", input_port_name="in2Add", output_port_name="outProd")
		self.CBD.addConnection("adderCBD", "productCBD", input_port_name="in1Prod", output_port_name="outAdd")
		self.CBD.addConnection("constantCBD2", "productCBD", input_port_name="in2Prod", output_port_name="outConstant2")
			
		self.CBD.flatten()
		self._run(5)
		self.assertEqual(self._getSignal("adderCBD.a"), [-0.75]*5)
		self.assertEqual(self._getSignal("productCBD.p"), [-3.75]*5)
		
	def testLinearStrongComponentWithNeg(self):
		CBDConstant1 = CBD("constantCBD1", output_ports = ["outConstant1"])
		CBDConstant1.addBlock(ConstantBlock(block_name="c", value=5))
		CBDConstant1.addConnection("c", "outConstant1")
		
		CBDConstant2 = CBD("constantCBD2", output_ports = ["outConstant2"])
		CBDConstant2.addBlock(ConstantBlock(block_name="c", value=8))
		CBDConstant2.addConnection("c", "outConstant2")
		
		CBDAdder1 = CBD("adder1CBD", input_ports = ["in1Add1", "in2Add1"], output_ports = ["outAdd1"])
		CBDAdder1.addBlock(AdderBlock(block_name="a"))
		CBDAdder1.addConnection("in1Add1", "a")
		CBDAdder1.addConnection("in2Add1", "a")
		CBDAdder1.addConnection("a", "outAdd1")
		
		CBDAdder2 = CBD("adder2CBD", input_ports = ["in1Add2", "in2Add2"], output_ports = ["outAdd2"])
		CBDAdder2.addBlock(AdderBlock(block_name="a"))
		CBDAdder2.addConnection("in1Add2", "a")
		CBDAdder2.addConnection("in2Add2", "a")
		CBDAdder2.addConnection("a", "outAdd2")
		
		CBDNegator = CBD("negatorCBD", input_ports = ["inNeg"], output_ports = ["outNeg"])
		CBDNegator.addBlock(NegatorBlock(block_name="n"))
		CBDNegator.addConnection("inNeg", "n")
		CBDNegator.addConnection("n", "outNeg")
		
		self.CBD.addBlock(CBDConstant1)
		self.CBD.addBlock(CBDConstant2)
		self.CBD.addBlock(CBDAdder1)
		self.CBD.addBlock(CBDAdder2)
		self.CBD.addBlock(CBDNegator)
		self.CBD.addConnection("constantCBD1", "adder1CBD", input_port_name="in1Add1", output_port_name="outConstant1")
		self.CBD.addConnection("adder2CBD", "adder1CBD", input_port_name="in2Add1", output_port_name="outAdd2")
		self.CBD.addConnection("constantCBD2", "adder2CBD", input_port_name="in1Add2", output_port_name="outConstant2")
		self.CBD.addConnection("negatorCBD", "adder2CBD", input_port_name="in2Add2", output_port_name="outNeg")
		self.CBD.addConnection("adder1CBD", "negatorCBD", input_port_name="inNeg", output_port_name="outAdd1")
		
		self.CBD.flatten()
		self._run(5)
		self.assertEqual(self._getSignal("adder1CBD.a"), [6.5]*5)
		self.assertEqual(self._getSignal("adder2CBD.a"), [1.5]*5)
		self.assertEqual(self._getSignal("negatorCBD.n"), [-6.5]*5)
		
	def testInterInterCBD(self):
		"""
							  +--------------------------------------------+
				   +----+     |                    +------+                |
				   |    |+--->|+------------------>|      |                |
				   |  2 |     ||                   |  +   +--------------->+-------+
		+----+     +----+     || +---------+   +-->|      |                |       |
		|    |                |+>|         |   |   +------+                |       v
		| 5  |   +------+     |  |         |   |                           |    +------+
		+----++->|      |     |  |    *    |   |                           |    |      |
				 |  +   |     |  |         |   |                           |    |  +   +------> 0
		+----++->|      |+--->|+>|         |   |                           |    |      |
		| 2  |   +------+     |  +--+------+   +--------------+            |    +------+
		|    |                |     |                         |   +-----+  |       ^
		+----+                |     |   +--------------------+|   |     |  |       |
							  |     |   |     +-----+        ||   | 12  +->+-------+
							  |     |   |     |     |        ||   |     |  |
							  |     +-->+---->|  -  +------->++   +-----+  |
							  |         |     |     |        |             |
							  |         |     +-----+        |             |
							  |         +--------------------+             |
							  +--------------------------------------------+
		"""		  
		CBDLittle1 = CBD("first_child", input_ports = ["in1CBD1", "in2CBD1"], output_ports = ["out1CBD1", "out2CBD1"])
		CBDLittle2 = CBD("first_child_of_first_child", input_ports = ["inCBD2"], output_ports = ["outCBD2"])
		
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=2.0))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=5.0))
		self.CBD.addBlock(ConstantBlock(block_name="c3", value=2.0))
		self.CBD.addBlock(AdderBlock(block_name="a"))
		self.CBD.addBlock(AdderBlock(block_name="a2"))
		self.CBD.addBlock(CBDLittle1)
		self.CBD.addConnection("c3", "a")
		self.CBD.addConnection("c2", "a")
		self.CBD.addConnection("c1", "first_child", input_port_name="in1CBD1")
		self.CBD.addConnection("a", "first_child", input_port_name="in2CBD1")
		self.CBD.addConnection("first_child", "a2", output_port_name="out1CBD1")
		self.CBD.addConnection("first_child", "a2", output_port_name="out2CBD1")
				
		CBDLittle1.addBlock(ProductBlock(block_name="p"))
		CBDLittle1.addBlock(AdderBlock(block_name="a"))
		CBDLittle1.addBlock(CBDLittle2)
		CBDLittle1.addBlock(ConstantBlock(block_name="c", value=12.0))
		CBDLittle1.addConnection("in1CBD1", "p")
		CBDLittle1.addConnection("in2CBD1", "p")
		CBDLittle1.addConnection("in1CBD1", "a")
		CBDLittle1.addConnection("first_child_of_first_child", "a", output_port_name="outCBD2")
		CBDLittle1.addConnection("p", "first_child_of_first_child", input_port_name="inCBD2")
		CBDLittle1.addConnection("c", "out1CBD1")
		CBDLittle1.addConnection("a", "out2CBD1")
		
		CBDLittle2.addBlock(NegatorBlock(block_name="n"))
		CBDLittle2.addConnection("inCBD2", "n")
		CBDLittle2.addConnection("n", "outCBD2")
		
		self.CBD.flatten()
		self._run(5)
		self.assertEqual(self._getSignal("first_child.p"), [14.0]*5)
		self.assertEqual(self._getSignal("first_child.first_child_of_first_child.n"), [-14.0]*5)
		self.assertEqual(self._getSignal("first_child.a"), [-12.0]*5)
		self.assertEqual(self._getSignal("a2"), [0.0]*5)

if __name__ == '__main__':  # pragma: no cover
	# When this module is executed from the command-line, run all its tests
    unittest.main()

	
	
	
	
	
	
	
