from pypdevs.DEVS import AtomicDEVS, CoupledDEVS
from pypdevs.infinity import INFINITY


class Scheduler(AtomicDEVS):
	def __init__(self, name, schedule):
		super(Scheduler, self).__init__(name)

		self.state = {
			"schedule": schedule,
			"index": 0,
			"time": 0.0
		}

		self.output = self.addOutPort("output")

	def timeAdvance(self):
		if self.state["index"] < len(self.state["schedule"]):
			time = self.state["schedule"][self.state["index"]][0]
			return time - self.state["time"]
		return INFINITY

	def intTransition(self):
		self.state["time"] += self.timeAdvance()
		self.state["index"] += 1
		return self.state

	def outputFnc(self):
		if self.state["index"] < len(self.state["schedule"]):
			evt = self.state["schedule"][self.state["index"]][1]
			return {
				self.output: evt
			}
		return {}

class TestCollector(AtomicDEVS):
	def __init__(self, name):
		super(TestCollector, self).__init__(name)
		self.state = {
			"time": 0,
			"data": []
		}
		self.inp = self.addInPort("inp")

	def get_data(self, idx):
		return self.state["data"][idx]

	def extTransition(self, inputs):
		self.state["time"] += self.elapsed
		if self.inp in inputs:
			self.state["data"].append([self.state["time"], inputs[self.inp]])
		return self.state


from components.messages import *

class PingPong(AtomicDEVS):
	def __init__(self, name, delay=0.0):
		super(PingPong, self).__init__(name)
		self.delay = delay

		self.state = {
			"item": None
		}

		self.inp = self.addInPort("inp")
		self.out = self.addOutPort("out")

	def timeAdvance(self):
		if self.state["item"] is None:
			return INFINITY
		return 0.1

	def outputFnc(self):
		if self.state["item"] is not None:
			return {
				self.out: QueryAck(self.state["item"].ID, self.delay)
			}
		return {}

	def intTransition(self):
		self.state["item"] = None
		return self.state

	def extTransition(self, inputs):
		if self.inp in inputs:
			self.state["item"] = inputs[self.inp]
		return self.state


class CDEVS(CoupledDEVS): pass