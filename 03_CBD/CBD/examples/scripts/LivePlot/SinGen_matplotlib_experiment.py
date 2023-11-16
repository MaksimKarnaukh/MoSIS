from SinGen import *
from pyCBD.realtime.plotting import PlotManager, LinePlot, follow
from pyCBD.simulator import Simulator
import matplotlib.pyplot as plt

sinGen = SinGen("sin")

fig = plt.figure(figsize=(5, 5), dpi=100)
ax = fig.add_subplot(111)
ax.set_ylim((-1, 1))    # The sine wave never exceeds this range
plot = fig, ax

manager = PlotManager()
manager.register("sin", sinGen.find('collector')[0], plot, LinePlot(color='red'))
# manager.connect('sin', 'update', lambda d, axis=ax: axis.set_xlim(follow(d[0], 10.0, lower_bound=0.0)))
manager.connect('sin', 'update', lambda d, p=plot: manager.set_xlim(p, follow(d[0], 10.0, lower_bound=0.0)))
# NOTE: alternatively, the pyCBD.realtime.plotting.set_xlim method can be used:
#   from pyCBD.realtime.plotting import set_xlim
#   manager.connect('sin', 'update', lambda d, p=plot: manager.set_xlim(p, follow(d[0], 10.0, lower_bound=0.0)))

sim = Simulator(sinGen)
sim.setRealTime()
sim.setDeltaT(0.1)
sim.run(20.0)

plt.show()
