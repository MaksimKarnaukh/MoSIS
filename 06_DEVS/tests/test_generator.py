import unittest

from tests.helpers import *

from components.generator import Generator

from pypdevs.simulator import Simulator


class TestGenerator(unittest.TestCase):
	def test_generator_normal(self):
		model = CDEVS("model")
		pp = model.addSubModel(PingPong("A"))
		gen = model.addSubModel(Generator("B", 5, 7, 10, 20, ["E"], limit=50))
		cl = model.addSubModel(TestCollector("cl"))
		model.connectPorts(gen.Q_send, pp.inp)
		model.connectPorts(pp.out, gen.Q_rack)
		model.connectPorts(gen.car_out, cl.inp)

		sim = Simulator(model)
		sim.setClassicDEVS()
		sim.simulate()

		cars = [x[1] for x in cl.state["data"]]
		self.assertEqual(len(cars), 50)

