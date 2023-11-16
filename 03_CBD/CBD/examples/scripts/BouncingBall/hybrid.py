from pyCBD.converters import hybrid
from BouncingBall import *
from pypdevs.DEVS import AtomicDEVS, CoupledDEVS
from pypdevs.infinity import INFINITY

class BouncingBall2(CBD):
	def __init__(self, k=0.7):
		super(BouncingBall2, self).__init__("BouncingBall", input_ports=["v0", "y0"], output_ports=["height", "velocity"])
		self.k = k

		self.addBlock(ConstantBlock("g", -9.81))
		self.addBlock(IntegratorBlock("v"))
		self.addBlock(IntegratorBlock("y"))

		self.addConnection("g", "v")
		self.addConnection("v", "y")
		self.addConnection("v", "velocity")
		self.addConnection("y", "height")
		self.addConnection("v0", "v", input_port_name="IC")
		self.addConnection("y0", "y", input_port_name="IC")


class Collector(AtomicDEVS):
	def __init__(self):
		super(Collector, self).__init__("Collector")
		self.state = {
			"time": 0.0,
			"v": [],
			"y": []
		}
		self.v = self.addInPort("v")
		self.y = self.addInPort("y")

	def extTransition(self, inputs):
		self.state["time"] += self.elapsed
		if self.v in inputs:
			self.state["v"].append((self.state["time"], inputs[self.v]))
		if self.y in inputs:
			self.state["y"].append((self.state["time"], inputs[self.y]))
		return self.state


class Bouncer(AtomicDEVS):
	def __init__(self):
		super(Bouncer, self).__init__("Bouncer")
		self.state = {
			"v": 0,
			"y": 0,
			"event": False
		}
		self.v = self.addInPort("v")
		self.y = self.addInPort("y")
		self.event = self.addInPort("event")
		self.bounce_v = self.addOutPort("bounce_v")
		self.bounce_y = self.addOutPort("bounce_y")

	def timeAdvance(self):
		if self.state["event"]:
			return 0
		return INFINITY

	def outputFnc(self):
		if self.state["event"]:
			return {
				self.bounce_v: -self.state["v"] * 0.7,
				self.bounce_y: 0.0
			}
		return {}

	def intTransition(self):
		self.state["event"] = False
		return self.state

	def extTransition(self, inputs):
		if self.v in inputs:
			self.state["v"] = inputs[self.v]
		if self.y in inputs:
			self.state["y"] = inputs[self.y]
		if self.event in inputs:
			self.state["event"] = True
		return self.state


class Model(CoupledDEVS):
	def __init__(self):
		super(Model, self).__init__("Model")

		ode = BouncingBall2()
		ode.addFixedRateClock(delta_t = 0.1)

		self.ball = self.addSubModel(hybrid.CBDRunner("ODE", ode, {
			"v0": 0.0, "y0": 100
		}, False, {
			"height": ">0"
		}, hybrid.CrossingDetection.ITP))
		self.coll = self.addSubModel(Collector())
		self.bounce = self.addSubModel(Bouncer())

		self.connectPorts(self.ball.outputs["velocity"], self.coll.v)
		self.connectPorts(self.ball.outputs["velocity"], self.bounce.v)
		self.connectPorts(self.ball.outputs["height"], self.coll.y)
		self.connectPorts(self.ball.outputs["height"], self.bounce.y)
		self.connectPorts(self.ball.outputs["crossing-height"], self.bounce.event)
		self.connectPorts(self.bounce.bounce_v, self.ball.inputs["v0"])
		self.connectPorts(self.bounce.bounce_y, self.ball.inputs["y0"])


CBD_POINTS = []
def bounce(e, t, model):
	if e.output_name == "height":
		CBD_POINTS.extend(model.getSignalHistory("height"))
		model.bounce()


if __name__ == '__main__':
	from pyCBD.simulator import Simulator as CBDsim
	from pyCBD.state_events import StateEvent, Direction
	from pyCBD.state_events.locators import LinearStateEventLocator
	import matplotlib.pyplot as plt

	plt.plot([0, 10], [0, 0], 'k--', zorder=0, lw=0.5)

	cbd = BouncingBall()
	csim = CBDsim(cbd)
	csim.setStateEventLocator(LinearStateEventLocator())
	csim.registerStateEvent(StateEvent("height", direction=Direction.FROM_ABOVE, event=bounce))
	csim.setDeltaT(0.1)
	csim.run(10.1)
	CBD_POINTS.extend(cbd.getSignalHistory("height"))
	ct, cy = [x[0] for x in CBD_POINTS], [x[1] for x in CBD_POINTS]
	plt.plot(ct, cy, '-o', label="CBD", zorder=1)

	from pypdevs.simulator import Simulator as DEVSsim

	model = Model()
	sim = DEVSsim(model)
	sim.setClassicDEVS(True)
	# sim.setVerbose(None)
	sim.setTerminationTime(10)
	sim.simulate()

	ty = model.coll.state["y"]
	t, y = [x[0] for x in ty], [x[1] for x in ty]
	plt.plot(t, y, '.', label="atomic DEVS", zorder=2)

	plt.tight_layout()
	plt.legend()
	plt.show()
