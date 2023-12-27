### Model
from pypdevs.DEVS import *

class TrafficLight(AtomicDEVS):
	def __init__(self):
		AtomicDEVS.__init__(self, "Light")
		self.state = "green"
		self.observe = self.addOutPort("observer")
		self.interrupt = self.addInPort("interrupt")

	def intTransition(self):
		state = self.state
		return {"red": "green",
			"yellow": "red",
			"green": "yellow"}[state]

	def timeAdvance(self):
		state = self.state
		return {"red": 60,
			"yellow": 3,
			"green": 57}[state]

	def outputFnc(self):
		state = self.state
		if state == "red":
			v = "green"
		elif state == "yellow":
			v = "red"
		elif state == "green":
			v = "yellow"
		return {self.observe: [v]}

	def extTransition(self, inputs):
		inp = inputs[self.interrupt][0]
		if inp == "manual":
			return "manual"
		elif inp == "auto":
			if self.state == "manual":
				return "red"

	def confTransition(self, inputs):
		self.elapsed = 0.0
		self.state = self.intTransition()
		self.state = self.extTransition(inputs)
		return self.state

### Experiment
from pypdevs.simulator import Simulator

model = TrafficLight()
sim = Simulator(model)

sim.setVerbose()
sim.setTerminationTime(500)

sim.simulate()