#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   /home/red/git/DrawioConvert/__main__.py Fibonacci.xml -F CBD -e FibonacciGen -gvaf

from SinGen import *
from pyCBD.simulator import Simulator
import matplotlib.pyplot as plt

plt.style.use('seaborn')


sinGen = SinGen("SinGen")
sim = Simulator(sinGen)

# Change this to change the Sin step size
sim.setDeltaT(0.1)
sim.setCommunicationInterval(0.333)
sim.setCustomTracer("tracerVCD", "VCDTracer", ("sine.vcd",))

# The termination time can be set as argument to the run call
sim.run(20.0)

# data = sinGen.getSignalHistory('OUT1')
# x, y = [x for x, _ in data], [y for _, y in data]
# # plt.plot(x, y, '--', c='black', lw=0.5, label="Signal")
# plt.scatter(x, y, 20, 'blue', 'o', label="Integration Points")
#
# import pandas as pd
# df = pd.read_csv("sine.csv")
# plt.scatter(df["time"], df["OUT1"], 15, 'red', 'X', label="Communication Points")
#
# plt.legend()
# plt.show()
