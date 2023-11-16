from SinGen import *
from pyCBD.realtime.plotting import PlotManager, LinePlot, follow
import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

fig = plt.figure(figsize=(15, 5), dpi=100)
ax = fig.add_subplot(111)
ax.set_ylim((-1, 1))

fig.tight_layout()

cbd = SinGen("SinGen")

root = tk.Tk()

canvas = FigureCanvasTkAgg(fig, master=root)  # A Tk DrawingArea
canvas.draw()
canvas.get_tk_widget().grid(column=1, row=1)

manager = PlotManager()
manager.register("sin", cbd.find("plot")[0], (fig, ax), LinePlot())
manager.connect('sin', 'update',
                lambda d, axis=ax: axis.set_xlim(follow(d[0], 10.0, lower_bound=0.0)))
manager.connect('sin', 'update',
                lambda d, axis=ax: axis.set_ylim(follow(d[1], lower_lim=-1.0, upper_lim=1.0)))

label = tk.Label(root, text="y = 1.00 * sin(1.00 * t)")
label.grid(column=1, row=2)

def set_amplitude(val):
	cbd.find("A")[0].setValue(float(val))
	update_label()

def set_period(val):
	cbd.find("B")[0].setValue(float(val))
	update_label()

def update_label():
	label["text"] = "y = {:.2f} * sin({:.2f} * t)".format(cbd.find("A")[0].getValue(),
	                                                      cbd.find("B")[0].getValue())

amplitude = tk.Scale(root, label="Amplitude", length=1200, orient=tk.HORIZONTAL, from_=0, to=5,
                     resolution=0.1, command=set_amplitude)
amplitude.set(1.0)
amplitude.grid(column=1, row=3)
period = tk.Scale(root, label="Period", length=1200, orient=tk.HORIZONTAL, from_=0, to=5,
                  resolution=0.1, command=set_period)
period.set(1.0)
period.grid(column=1, row=4)

from pyCBD.simulator import Simulator

sim = Simulator(cbd)
sim.setRealTime()
sim.setRealTimePlatformTk(root)
# sim.setTerminationTime(10)
sim.setDeltaT(0.1)
sim.run()
root.mainloop()
