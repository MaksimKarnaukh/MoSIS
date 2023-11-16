#!/usr/bin/env python
#
# Unit tests for the sorting of a CBD.

import unittest
from pyCBD.Core import *
from pyCBD.lib.std import *
from pyCBD.depGraph import createDepGraph
from pyCBD.simulator import Simulator
from pyCBD.scheduling import TopologicalScheduler

class SortedGraphCBDTest(unittest.TestCase):
	def setUp(self):
		self.CBD = CBD("block_under_test")
		self.sim = Simulator(self.CBD)
		self.scheduler = TopologicalScheduler()

	def testSortedGraph(self):
		CBDNegator = CBD("negatorCBD", input_ports = ["inNegator"], output_ports = ["outNegator"])
		negCbd = NegatorBlock(block_name="nC")
		CBDNegator.addBlock(negCbd)
		CBDNegator.addConnection("inNegator", "nC")
		CBDNegator.addConnection("nC", "outNegator")

		const = ConstantBlock(block_name="c", value=5.5)
		self.CBD.addBlock(const)
		neg = NegatorBlock(block_name="n")
		self.CBD.addBlock(neg)
		self.CBD.addBlock(CBDNegator)
		self.CBD.addConnection("negatorCBD", "n", output_port_name="outNegator")
		self.CBD.addConnection("c", "negatorCBD", input_port_name="inNegator")
		
		depGraph = createDepGraph(self.CBD, 0)
		sortedGraph = self.scheduler.obtain(depGraph, 1, 0.0)
		
		self.assertEqual(len(sortedGraph), 3)
		self.assertEqual(sortedGraph[0][0], const)
		self.assertEqual(sortedGraph[1][0], negCbd)
		self.assertEqual(sortedGraph[2][0], neg)
		
	def testSortedGraph2(self):
		CBDAdder = CBD("adderCBD", input_ports = ["in1", "in2"], output_ports = ["outAdd"])
		addCBD = AdderBlock(block_name="aC")
		CBDAdder.addBlock(addCBD)
		CBDAdder.addConnection("in1", "aC")
		CBDAdder.addConnection("in2", "aC")
		CBDAdder.addConnection("aC", "outAdd")

		const1 = ConstantBlock(block_name="c1", value=5.5)
		const2 = ConstantBlock(block_name="c2", value=4.5)
		self.CBD.addBlock(const1)
		self.CBD.addBlock(const2)
		neg = NegatorBlock(block_name="n")
		self.CBD.addBlock(neg)
		self.CBD.addBlock(CBDAdder)
		self.CBD.addConnection("adderCBD", "n", output_port_name="outAdd")
		self.CBD.addConnection("c1", "adderCBD", input_port_name="in1")
		self.CBD.addConnection("c2", "adderCBD", input_port_name="in2")
		
		depGraph = createDepGraph(self.CBD, 0)
		sortedGraph = self.scheduler.obtain(depGraph, 1, 0.0)
		comps = [ x[0] for x in sortedGraph ]
		
		tester = self
		ag = lambda x,y: tester.assertTrue(comps.index(x) > comps.index(y))
		
		self.assertEqual(len(sortedGraph), 4)
		ag(addCBD, const1)
		ag(addCBD, const2)
		ag(neg, addCBD)
		
	def testSortedGraph3(self):	
		CBDNegator = CBD("negatorCBD", input_ports = ["inNegator"], output_ports = ["outNegator", "outInverter"])
		negCbd = NegatorBlock(block_name="nC")
		invCBD = InverterBlock(block_name="iC")
		CBDNegator.addBlock(negCbd)
		CBDNegator.addBlock(invCBD)
		CBDNegator.addConnection("inNegator", "nC")
		CBDNegator.addConnection("inNegator", "iC")
		CBDNegator.addConnection("nC", "outNegator")
		CBDNegator.addConnection("iC", "outInverter")

		const = ConstantBlock(block_name="c", value=5.5)
		self.CBD.addBlock(const)
		add = AdderBlock(block_name="a")
		self.CBD.addBlock(add)
		self.CBD.addBlock(CBDNegator)
		self.CBD.addConnection("negatorCBD", "a", output_port_name="outNegator")
		self.CBD.addConnection("negatorCBD", "a", output_port_name="outInverter")
		self.CBD.addConnection("c", "negatorCBD", input_port_name="inNegator")
		
		depGraph = createDepGraph(self.CBD, 0)
		sortedGraph = self.scheduler.obtain(depGraph, 1, 0.0)
		comps = [ x[0] for x in sortedGraph ]
		
		tester = self
		ag = lambda x,y: tester.assertTrue(comps.index(x) > comps.index(y))

		self.assertEqual(len(sortedGraph), 4)
		ag(negCbd, const)
		ag(invCBD, const)
		ag(add, negCbd)
		ag(add, invCBD)
		
	def testSortedGraph4(self):
		CBDStrong = CBD("strongCBD", input_ports = ["inC1", "inC2"], output_ports = [])
		CBDStrong.addBlock(AdderBlock(block_name="a1"))
		CBDStrong.addBlock(AdderBlock(block_name="a3"))
		CBDStrong.addBlock(AdderBlock(block_name="a2"))
		CBDStrong.addConnection("a3", "a1")
		CBDStrong.addConnection("a1", "a3")
		CBDStrong.addConnection("a2", "a3")
		CBDStrong.addConnection("inC1", "a1")
		CBDStrong.addConnection("inC2", "a2")
		CBDStrong.addConnection("a3", "a2")
		
		self.CBD.addBlock(CBDStrong)
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=5.5))
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=-5))
		self.CBD.addConnection("c1", "strongCBD", input_port_name="inC1")
		self.CBD.addConnection("c2", "strongCBD", input_port_name="inC2")
		
		depGraph = createDepGraph(self.CBD, 0)
		sortedGraph = self.scheduler.obtain(depGraph, 1, 0.0)
				
		self.assertEqual(len(sortedGraph), 3)
		self.assertEqual(len(sortedGraph[2]), 3)
		
	def testSortedGraph5(self):
		CBDStrong = CBD("strongCBD", input_ports = ["inC1", "inC2", "inA"], output_ports = ["out1", "out2"])
		CBDStrong.addBlock(AdderBlock(block_name="a1"))
		CBDStrong.addBlock(AdderBlock(block_name="a2"))
		CBDStrong.addConnection("inA", "a1")
		CBDStrong.addConnection("a1", "out1")
		CBDStrong.addConnection("a2", "out2")
		CBDStrong.addConnection("inC1", "a1")
		CBDStrong.addConnection("inC2", "a2")
		CBDStrong.addConnection("inA", "a2")
		
		self.CBD.addBlock(CBDStrong)
		self.CBD.addBlock(AdderBlock(block_name="a3"))
		self.CBD.addBlock(ConstantBlock(block_name="c2", value=5.5))
		self.CBD.addBlock(ConstantBlock(block_name="c1", value=-5))
		self.CBD.addConnection("c1", "strongCBD", input_port_name="inC1")
		self.CBD.addConnection("c2", "strongCBD", input_port_name="inC2")
		self.CBD.addConnection("a3", "strongCBD", input_port_name="inA")
		self.CBD.addConnection("strongCBD", "a3", output_port_name="out1")
		self.CBD.addConnection("strongCBD", "a3", output_port_name="out2")
		
		depGraph = createDepGraph(self.CBD, 0)
		sortedGraph = self.scheduler.obtain(depGraph, 1, 0.0)
				
		self.assertEqual(len(sortedGraph), 3)
		self.assertEqual(len(sortedGraph[2]), 3)

	def testAlwaysRecomputeSchedule(self):
		self.scheduler.recompte_at = True
		self.testSortedGraph()

	def testSometimesRecomputeSchedule(self):
		self.scheduler.recompte_at = [0, 4]
		self.testSortedGraph()

if __name__ == '__main__':  # pragma: no cover
	# When this module is executed from the command-line, run all its tests
	unittest.main()

	
	
	
	
	
	
	
