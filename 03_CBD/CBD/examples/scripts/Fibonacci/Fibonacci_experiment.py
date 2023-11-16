#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   /home/red/git/DrawioConvert/__main__.py Fibonacci.xml -F CBD -e FibonacciGen -gvaf

from Fibonacci import *
from pyCBD.simulator import Simulator
import matplotlib.pyplot as plt


cbd = FibonacciGen("FibonacciGen")

# Run the Simulation
sim = Simulator(cbd)
sim.setVerbose(None)
sim.run(10)

data = cbd.getSignalHistory('OUT1')
t, v = [t for t, _ in data], [v for _, v in data]

print(v)

fig = plt.figure()
ax = fig.subplots()
ax.set_title("Fibonacci Numbers")
ax.set_xlabel("N")
ax.set_ylabel("Value")
ax.scatter(t, v)
plt.show()
