import unittest

from tests.helpers import *
from components.fork import Fork
from components.messages import *

from pypdevs.simulator import Simulator

class TestFork(unittest.TestCase):
	def test_fork_normal(self):
		model = CDEVS("model")
		sc = model.addSubModel(Scheduler("sc", [
			(2, Car(1, 15, 5, 5, v=15)),
			(3, Car(2, 15, 5, 5, v=15, no_gas=True)),
			(4, Car(3, 15, 5, 5, v=15, no_gas=True)),
			(5, Car(4, 15, 5, 5, v=15)),
			(6, Car(5, 15, 5, 5, v=15, no_gas=True))
		]))
		rs = model.addSubModel(Fork("rs", 10, 15))
		cl1 = model.addSubModel(TestCollector("cl1"))
		cl2 = model.addSubModel(TestCollector("cl2"))
		model.connectPorts(sc.output, rs.car_in)
		model.connectPorts(rs.car_out, cl1.inp)
		model.connectPorts(rs.car_out2, cl2.inp)

		sim = Simulator(model)
		sim.setClassicDEVS()
		sim.simulate()

		self.assertEqual(len(cl1.state["data"]), 2)
		self.assertListEqual([c[1].v for c in cl1.state["data"]], [15] * 2)
		self.assertListEqual([c[1].distance_traveled for c in cl1.state["data"]], [rs.L] * 2)
		self.assertEqual([c[1].ID for c in cl1.state["data"]], [1, 4])
		self.assertEqual(len(cl2.state["data"]), 3)
		self.assertListEqual([c[1].v for c in cl2.state["data"]], [15] * 3)
		self.assertListEqual([c[1].distance_traveled for c in cl2.state["data"]], [rs.L] * 3)
		self.assertEqual([c[1].ID for c in cl2.state["data"]], [2, 3, 5])

