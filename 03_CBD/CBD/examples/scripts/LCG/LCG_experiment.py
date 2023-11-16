#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   /home/red/git/DrawioConvert/__main__.py LCG.xml -av -F CBD -e LCG -t 30

from pyCBD.simulator import Simulator
from LCG import *
import matplotlib.pyplot as plt

def term(model, _):
	signals = [y for __, y in model.getSignalHistory("OUT1")]
	unique_signals = set(signals)
	return len(signals) > len(unique_signals)

lcg = LCG("LCG", 1, 4, 9, 0)

# Run the Simulation
sim = Simulator(lcg)
sim.setTerminationCondition(term)
sim.run()

# Print a full cycle: [0, 4, 8, 3, 7, 2, 6, 1, 5]
print([v for _, v in lcg.getSignalHistory("OUT1")])

data = lcg.getSignalHistory('OUT1')
x, y = [x for x, _ in data], [y for _, y in data]

plt.scatter(x, y, s=5)
plt.show()
