import unittest

from tests.helpers import *

# from components.generator import uuid
import uuid
from components.roadsegment import RoadSegment
from components.messages import *

from pypdevs.simulator import Simulator

class TestRoadSegment(unittest.TestCase):
	def test_roadsegment_normal(self):
		model = CDEVS("model")
		sc = model.addSubModel(Scheduler("sc", [(2, Car(uuid.uuid4(), 15, 5, 5, v=15))]))
		rs = model.addSubModel(RoadSegment("rs", 10, 15))
		cl = model.addSubModel(TestCollector("cl"))
		model.connectPorts(sc.output, rs.car_in)
		model.connectPorts(rs.car_out, cl.inp)
		cls = model.addSubModel(TestCollector("cls"))
		model.connectPorts(rs.Q_send, cls.inp)

		sim = Simulator(model)
		sim.setClassicDEVS()
		sim.simulate()

		self.assertEqual(len(cl.state["data"]), 1)
		self.assertEqual(cl.get_data(0)[1].distance_traveled, rs.L)
		self.assertEqual(cl.get_data(0)[1].v, 15)
		self.assertAlmostEqual(cl.get_data(0)[0], 2 / 3 + 2, 4)
		self.assertEqual(cls.get_data(0)[0], 2)

	def test_roadsegment_decelerate_road(self):
		model = CDEVS("model")
		car = Car(uuid.uuid4(), 15, 5, 5, v=15)
		sc1 = model.addSubModel(Scheduler("sc1", [(2, car)]))
		sc2 = model.addSubModel(Scheduler("sc2", [(2.1, QueryAck(car.ID, 0.0))]))
		rs = model.addSubModel(RoadSegment("rs", 10, 10))
		cl = model.addSubModel(TestCollector("cl"))
		model.connectPorts(sc1.output, rs.car_in)
		model.connectPorts(sc2.output, rs.Q_rack)
		model.connectPorts(rs.car_out, cl.inp)
		cls = model.addSubModel(TestCollector("cls"))
		model.connectPorts(rs.Q_send, cls.inp)

		sim = Simulator(model)
		sim.setClassicDEVS()
		sim.simulate()

		self.assertEqual(len(cl.state["data"]), 1)
		self.assertEqual(cl.get_data(0)[1].distance_traveled, rs.L)
		self.assertEqual(cl.get_data(0)[1].v, 10)
		self.assertAlmostEqual(cl.get_data(0)[0], 2.95, 4)
		self.assertEqual(cls.get_data(0)[0], 2)

	def test_roadsegment_accelerate_road(self):
		model = CDEVS("model")
		car = Car(uuid.uuid4(), 30, 5, 5, v=15)
		sc1 = model.addSubModel(Scheduler("sc1", [(2, car)]))
		sc2 = model.addSubModel(Scheduler("sc2", [(2.1, QueryAck(car.ID, 0.0))]))
		rs = model.addSubModel(RoadSegment("rs", 10, 20))
		cl = model.addSubModel(TestCollector("cl"))
		model.connectPorts(sc1.output, rs.car_in)
		model.connectPorts(sc2.output, rs.Q_rack)
		model.connectPorts(rs.car_out, cl.inp)
		cls = model.addSubModel(TestCollector("cls"))
		model.connectPorts(rs.Q_send, cls.inp)

		sim = Simulator(model)
		sim.setClassicDEVS()
		sim.simulate()

		self.assertEqual(len(cl.state["data"]), 1)
		self.assertEqual(cl.get_data(0)[1].distance_traveled, rs.L)
		self.assertEqual(cl.get_data(0)[1].v, 20)
		self.assertAlmostEqual(cl.get_data(0)[0], 2.525, 4)
		self.assertEqual(cls.get_data(0)[0], 2)

	def test_roadsegment_crash(self):
		model = CDEVS("model")
		car1 = Car(uuid.uuid4(), 30, 5, 5, v=0)
		car2 = Car(uuid.uuid4(), 30, 5, 5, v=10)
		rs = model.addSubModel(RoadSegment("rs", 10, 20))
		rs.car_enter(car1)
		sc1 = model.addSubModel(Scheduler("sc1", [(2, car2)]))
		model.connectPorts(sc1.output, rs.car_in)

		sim = Simulator(model)
		sim.setClassicDEVS()
		sim.simulate()

		self.assertEqual(rs.state.collisions, 1)
		self.assertEqual(len(rs.state.cars_present), 0)

	def test_roadsegment_merge(self):
		model = CDEVS("model")
		sc1 = model.addSubModel(Scheduler("sc1", [(2, Car(1, 15, 5, 5, v=15))]))
		sc2 = model.addSubModel(Scheduler("Asc2", [(3, QueryAck(1, 0.0)), (3, QueryAck(1, 0.5, sideways=True))]))
		rs = model.addSubModel(RoadSegment("Brs", 30, 15))
		cl = model.addSubModel(TestCollector("cl"))
		model.connectPorts(sc1.output, rs.car_in)
		model.connectPorts(sc2.output, rs.Q_rack)
		model.connectPorts(rs.car_out, cl.inp)

		sim = Simulator(model)
		sim.setClassicDEVS()
		sim.simulate()

		self.assertEqual(cl.get_data(0)[0], 4.5)
		self.assertEqual(cl.get_data(0)[1].v, 10)

