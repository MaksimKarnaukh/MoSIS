import unittest

from tests.helpers import *

from components.sidemarker import SideMarker
from components.messages import QueryAck

from pypdevs.simulator import Simulator


class TestSideMarker(unittest.TestCase):
	def test_sidemarker_normal(self):
		model = CDEVS("model")
		sc = model.addSubModel(Scheduler("sc", [
			(1, QueryAck(1, 0.0)),
			(2, QueryAck(2, 0.0)),
			(3, QueryAck(3, 0.0))
		]))
		sm = model.addSubModel(SideMarker("sm"))
		cl = model.addSubModel(TestCollector("cl"))
		model.connectPorts(sc.output, sm.mi)
		model.connectPorts(sm.mo, cl.inp)

		sim = Simulator(model)

		sim.setClassicDEVS()
		sim.setTerminationTime(10)
		sim.simulate()

		self.assertTrue(all([a[1].sideways for a in cl.state["data"]]))

