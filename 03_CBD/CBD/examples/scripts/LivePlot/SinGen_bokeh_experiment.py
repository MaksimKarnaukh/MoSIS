from SinGen import *
from pyCBD.realtime.plotting import PlotManager, Backend, StepPlot, follow
from pyCBD.simulator import Simulator
import sys, logging

from bokeh.plotting import figure, curdoc

sinGen = SinGen("sin")

fig = figure(plot_width=500, plot_height=500, x_range=(0, 0), y_range=(-1, 1))
document = curdoc()
document.add_root(fig)

# Use the Bokeh Backend
manager = PlotManager(Backend.BOKEH)
manager.register("sin", sinGen.find('collector')[0], fig, StepPlot(color='green', line_width=3))

manager.connect('sin', 'update', lambda d:
					manager.bokeh_set_xlim(fig, document, follow(d[0], 10.0, lower_bound=0.0)))

sim = Simulator(sinGen)
sim.connect("finished", manager.stop)
sim.setRealTime()
sim.setDeltaT(0.1)
sim.run(200.0)
