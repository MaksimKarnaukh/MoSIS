from pyCBD.Core import *
from pyCBD.lib.std import *
from pyCBD.lib.endpoints import SignalCollectorBlock

class BouncingBall(CBD):
	def __init__(self, k=0.7, v0=0, y0=100):
		super(BouncingBall, self).__init__("BouncingBall", output_ports=["height", "velocity"])
		self.k = k

		self.addBlock(ConstantBlock("g", -9.81))
		self.addBlock(ConstantBlock("v0", v0))
		self.addBlock(ConstantBlock("y0", y0))
		self.addBlock(IntegratorBlock("v"))
		self.addBlock(IntegratorBlock("y"))
		self.addBlock(SignalCollectorBlock("plot1"))
		self.addBlock(SignalCollectorBlock("plot2"))

		self.addConnection("g", "v")
		self.addConnection("v", "y")
		self.addConnection("v", "velocity")
		self.addConnection("y", "height")
		self.addConnection("y", "plot1")
		self.addConnection("v", "plot2")
		self.addConnection("v0", "v", input_port_name="IC")
		self.addConnection("y0", "y", input_port_name="IC")

	def bounce(self):
		v_pre = self.getSignalHistory("velocity")[-1].value
		v_new = -v_pre * self.k
		self.getBlockByName("v0").setValue(v_new)
		self.getBlockByName("y0").setValue(0.0)