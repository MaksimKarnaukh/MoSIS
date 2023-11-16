from BouncingBall import *
from pyCBD.realtime.plotting import PlotManager, LinePlot
from pyCBD.simulator import Simulator
import matplotlib.pyplot as plt

bb = BouncingBall()

DELTA = 0.1
TIME = 15.0

fig = plt.figure(figsize=(5, 5), dpi=100)
ax1 = fig.add_subplot(111)
# ax2 = fig.add_subplot(122)
ax1.set_xlim((0, TIME))
ax1.set_ylim((-1, 105))
ax1.set_xlabel("time")
ax1.set_ylabel("height")
# ax2.set_xlim((0, TIME))
# ax2.set_ylim((-50, 50))
# ax2.set_ylabel("velocity")
plot1 = fig, ax1
# plot2 = fig, ax2

ax1.plot((0, TIME+DELTA), (0, 0), c='purple', ls='--', lw=0.1)

manager = PlotManager()
manager.register("height", bb.getBlockByName('plot1'), plot1, LinePlot(color='red'))
# manager.register("velocity", bb.getBlockByName('plot2'), plot2, LinePlot(color='blue'))

from pyCBD.state_events import StateEvent, Direction
from pyCBD.state_events.locators import *

def bounce(e, t, model):
	if e.output_name == "height":
		model.bounce()
		print("BOUNCE AT:", t)
	else:
		y = model.getSignalHistory("height")[-1].value
		model.getBlockByName("y0").setValue(y)
		model.getBlockByName("v0").setValue(-41)

lengs = []
times = []

def poststep(o, t, st):
	times.append(st)
	lengs.append(t - o)

sim = Simulator(bb)
sim.setStateEventLocator(ITPStateEventLocator())
sim.registerStateEvent(StateEvent("height", direction=Direction.FROM_ABOVE, event=bounce))
# sim.registerStateEvent(StateEvent("velocity", direction=Direction.FROM_ABOVE, level=-40.0, event=bounce))
sim.connect("poststep", poststep)
sim.setRealTime()
sim.setDeltaT(DELTA)
sim.run(TIME)

# import time
# while sim.is_running():
# 	time.sleep(0.1)

plt.show()

import numpy as np

fig = plt.figure(figsize=(5, 5), dpi=100)
ax = fig.add_subplot(111)
ax.set_xticks(np.arange(0, TIME, DELTA), minor=True)
ax.set_xlim((0, TIME+DELTA))

ax.bar(times, lengs, width=0.05, color='green', label='duration')
# ax.plot((0, TIME+DELTA), (DELTA, DELTA), c='red', ls='--')

ax2 = ax.twinx()
ax2.set_ylim((0, 105))
ax2.plot(*bb.getBlockByName('plot1').data_xy, c='blue', label='simulation')

handles, labels = ax.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()

ax.legend(handles + handles2, labels + labels2)
plt.show()
