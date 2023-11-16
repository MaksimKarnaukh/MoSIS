from pyCBD.Core import CBD
from pyCBD.lib.std import *

class Test(CBD):
	def __init__(self, name):
		CBD.__init__(self, name, [], ["x", "y"])
		# self.addBlock(AdderBlock("sum"))
		# self.addBlock(ConstantBlock("three", 3.0))
		self.addBlock(TimeBlock("three"))
		# self.addBlock(ConstantBlock("seven", 7))
		self.addBlock(ProductBlock("mult", 3))

		self.addConnection("three", "mult")
		self.addConnection("mult", "mult")
		self.addConnection("mult", "mult")
		self.addConnection("mult", "x")
		self.addConnection("mult", "y")

		# self.addConnection("three", "sum")
		# self.addConnection("mult", "sum")
		# self.addConnection("sum", "x")
		# self.addConnection("seven", "mult")
		# self.addConnection("sum", "mult")
		# self.addConnection("mult", "y")

if __name__ == '__main__':
	test = Test("test")

	from pyCBD.simulator import Simulator
	from pyCBD.loopsolvers.sympysolver import SympySolver
	import time

	durations = []
	pre = 0.0

	def prestep():
		global pre
		pre = time.time()

	def poststep():
		durations.append(time.time() - pre)

	delta = 1
	length = 50
	sim = Simulator(test)
	sim.setDeltaT(delta)
	sim.setAlgebraicLoopSolver(SympySolver())
	# sim.setRealTime()
	# sim.setProgressBar()
	sim.connect("prestep", prestep)
	sim.connect("poststep", poststep)
	start = time.time()
	sim.run(length)

	# while sim.is_running(): pass

	print("Duration:", time.time() - start)
	import matplotlib.pyplot as plt
	plt.bar(list(range(int(length / delta))), durations)
	plt.plot([0.0, length / delta], [delta, delta], color="red")
	plt.show()

	print()
	print("X", test.getSignalHistory("x"))
	print("Y", test.getSignalHistory("y"))

	# C code gen testing:
	# from pyCBD.converters.CBD2C import CBD2C
	# gen = CBD2C(test, 100)
	# gen.generate("example.c")
