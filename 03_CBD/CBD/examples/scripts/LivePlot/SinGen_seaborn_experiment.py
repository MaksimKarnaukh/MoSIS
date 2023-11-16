from SinGen import *
from pyCBD.realtime.plotting import PlotManager, LinePlot, follow, Backend
from pyCBD.simulator import Simulator
import matplotlib.pyplot as plt

sinGen = SinGen("sin")

import seaborn as sns
sns.set_theme(style="darkgrid")

fig = plt.figure(figsize=(5, 5), dpi=100)
ax = fig.add_subplot(111)
ax.set_ylim((-1, 1))    # The sine wave never exceeds this range

manager = PlotManager(Backend.SEABORN)
manager.register("sin", sinGen.find('collector')[0], (fig, ax), LinePlot(color='red'))
manager.connect('sin', 'update', lambda d, axis=ax: axis.set_xlim(follow(d[0], 10.0, lower_bound=0.0)))

sim = Simulator(sinGen)
sim.setRealTime()
sim.setDeltaT(0.1)
sim.run(20.0)

plt.show()
