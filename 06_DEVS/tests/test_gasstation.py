import unittest

from tests.helpers import *

from components.gasstation import GasStation
from components.messages import *

from pypdevs.simulator import Simulator

class TestGasStation(unittest.TestCase):
	def test_gasstation_normal(self):
		model = CDEVS("model")
		sc = model.addSubModel(Scheduler("sc", [(x, Car(x, 15, 5, 5, v=15, departure_time=x)) for x in range(1000)]))
		pp = model.addSubModel(PingPong("pp"))
		gs = model.addSubModel(GasStation("gs"))
		cl = model.addSubModel(TestCollector("cl"))
		model.connectPorts(sc.output, gs.car_in)
		model.connectPorts(gs.Q_send, pp.inp)
		model.connectPorts(pp.out, gs.Q_rack)
		model.connectPorts(gs.car_out, cl.inp)

		sim = Simulator(model)
		sim.setClassicDEVS()
		sim.simulate()

		times = [x[0] - x[1].departure_time for x in cl.state["data"]]
		cars = [x[1] for x in cl.state["data"]]

		self.assertSetEqual(set(c.ID for c in cars), set(x for x in range(1000)))

		avg_time = sum(times) / len(times)
		self.assertTrue(580 < avg_time < 620)
		self.assertGreaterEqual(min(times), 120)

