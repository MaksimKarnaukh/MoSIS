#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   /home/red/git/DrawioConvert/__main__.py EvenNumberGen.xml -av -F CBD -e LCG -t 30 -f

from pyCBD.lib.endpoints import SignalCollectorBlock
from EvenNumberGen import *
from pyCBD.simulator import Simulator
import matplotlib.pyplot as plt

cbd = EvenNumberGen("gen")

# Run the Simulation
sim = Simulator(cbd)
sim.run(30.0)

data = cbd.getSignalHistory('OUT1')
x, y = [x for x, _ in data], [y for _, y in data]

plt.scatter(x, y)
plt.show()
