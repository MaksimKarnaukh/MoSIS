#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   /home/red/git/DrawioConvert/__main__.py LCG.xml -av -F CBD -e LCG -t 30

# from CBD.lib.plotting import SignalPlotBlock
from pyCBD.simulator import Simulator
from LCG import *
import matplotlib.pyplot as plt
from pyCBD.realtime.plotting import PlotManager, ScatterPlot, follow

fig = plt.figure(figsize=(15, 5), dpi=100)
ax = fig.add_subplot(1, 1, 1)
ax.set_ylim((0, 9))

cbd = LCG("LCG")

manager = PlotManager()
manager.register("lcg", cbd.find('collector')[0], (fig, ax), ScatterPlot())
manager.connect('lcg', 'update', lambda d, axis=ax: axis.set_xlim(follow(d[0], 10.0, lower_bound=0.0)))


# Run the Simulation
sim = Simulator(cbd)
sim.setRealTime()
sim.setProgressBar()
sim.run(30.0)

plt.show()
# while sim.is_running(): pass
