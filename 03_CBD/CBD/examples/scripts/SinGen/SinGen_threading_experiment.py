#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   /home/red/git/DrawioConvert/__main__.py Fibonacci.xml -F CBD -e FibonacciGen -gvaf

from SinGen import *
from pyCBD.simulator import Simulator
import matplotlib.pyplot as plt


sinGen = SinGen("SinGen")
sim = Simulator(sinGen)
sim.setProgressBar()
sim.setRealTime()
sim.setRealTimePlatformThreading()
sim.setDeltaT(0.3)
sim.run(100.0)

# Keep it alive
while sim.is_running(): pass

print("FINISHED!")

data = sinGen.getSignalHistory('OUT1')
x, y = [x for x, _ in data], [y for _, y in data]

plt.plot(x, y)
plt.show()
