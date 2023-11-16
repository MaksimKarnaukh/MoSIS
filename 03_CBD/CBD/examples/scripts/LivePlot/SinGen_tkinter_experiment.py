from SinGen import *
from pyCBD.realtime.plotting import PlotManager, LinePlot, follow
from pyCBD.simulator import Simulator

import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

sinGen = SinGen("sin")

fig = plt.figure(figsize=(5, 5), dpi=100)
ax = fig.add_subplot(111)
ax.set_ylim((-1, 1))    # The sine wave never exceeds this range

root = tk.Tk()

# Create a canvas to gvDraw the plot on
canvas = FigureCanvasTkAgg(fig, master=root)  # A Tk DrawingArea
canvas.draw()
canvas.get_tk_widget().grid(column=1, row=1)

manager = PlotManager()
manager.register("sin", sinGen.find('collector')[0], (fig, ax), LinePlot(color='red'))
manager.connect('sin', 'update', lambda d, axis=ax: axis.set_xlim(follow(d[0], 10.0, lower_bound=0.0)))

sim = Simulator(sinGen)
sim.setRealTime()
sim.setRealTimePlatformTk(root)
sim.setDeltaT(0.1)
sim.run(20.0)

root.mainloop()
