import unittest

from tests.helpers import *
from components.crossroads import CrossRoadSegment
from components.messages import *

from pypdevs.simulator import Simulator

class TestCrossRoadSegment(unittest.TestCase):
	def test_crossroadsegment_normal(self):
		model = CDEVS("model")
		sc1 = model.addSubModel(Scheduler("sc", [
			(2, Car(1, 15, 5, 5, v=15, destination="R")),
			(3, Car(2, 15, 5, 5, v=15, destination="L")),
			(5, Car(4, 15, 5, 5, v=15, destination="L"))
		]))
		sc2 = model.addSubModel(Scheduler("sc", [
			(4, Car(3, 15, 5, 5, v=15, destination="R")),
			(6, Car(5, 15, 5, 5, v=15, destination="R"))
		]))
		rs = model.addSubModel(CrossRoadSegment("rs", 10, 15, destinations=["R"]))
		cl1 = model.addSubModel(TestCollector("cl1"))
		cl2 = model.addSubModel(TestCollector("cl2"))
		model.connectPorts(sc1.output, rs.car_in)
		model.connectPorts(sc2.output, rs.car_in_cr)
		model.connectPorts(rs.car_out, cl1.inp)
		model.connectPorts(rs.car_out_cr, cl2.inp)

		sim = Simulator(model)
		sim.setClassicDEVS()
		sim.simulate()

		self.assertEqual(len(cl1.state["data"]), 3)
		self.assertListEqual([c[1].v for c in cl1.state["data"]], [15] * 3)
		self.assertListEqual([c[1].distance_traveled for c in cl1.state["data"]], [rs.L] * 3)
		self.assertEqual([c[1].ID for c in cl1.state["data"]], [1, 3, 5])
		self.assertEqual(len(cl2.state["data"]), 2)
		self.assertListEqual([c[1].v for c in cl2.state["data"]], [15] * 2)
		self.assertListEqual([c[1].distance_traveled for c in cl2.state["data"]], [rs.L] * 2)
		self.assertEqual([c[1].ID for c in cl2.state["data"]], [2, 4])

