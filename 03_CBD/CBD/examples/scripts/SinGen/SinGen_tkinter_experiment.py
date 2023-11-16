#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   /home/red/git/DrawioConvert/__main__.py Fibonacci.xml -F CBD -e FibonacciGen -gvaf

from SinGen import *
from pyCBD.simulator import Simulator
import matplotlib.pyplot as plt
import tkinter as tk

root = tk.Tk()
sinGen = SinGen("SinGen")
sim = Simulator(sinGen)
# sim.setProgressBar()
sim.setRealTime()
sim.setRealTimePlatformTk(root)
sim.setDeltaT(0.3)
sim.run(100.0)

root.mainloop()

print("FINISHED!")

data = sinGen.getSignalHistory('OUT1')
x, y = [x for x, _ in data], [y for _, y in data]

plt.plot(x, y)
plt.show()
