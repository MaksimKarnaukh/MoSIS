TkInter Dashboard with Editable Values
======================================
Often, users would like to have interaction with certain values during the simulation.
This reduces the need to run multiple simulations in which only small values need to
be changed. Seeing as the simulator provides a way of interacting with TkInter, building
such a dashboard is quite easy.

Example Model
-------------
The normal :doc:`SinGen` will be slightly extended to comply to the following (more generic)
formula:

.. math::

    y(t) = A \cdot \sin(B \cdot t)

The CBD model therefore becomes:

.. code-block:: python

    from CBD.Core import CBD
    from CBD.lib.std import *
    from CBD.lib.endpoints import SignalCollectorBlock

    class SinGen(CBD):
        def __init__(self, block_name):
            CBD.__init__(self, block_name, input_ports=[], output_ports=[])

            # Create the Blocks
            self.addBlock(TimeBlock("time"))
            self.addBlock(GenericBlock("sin", block_operator=("sin")))
            self.addBlock(ConstantBlock("A", 1.0))
            self.addBlock(ConstantBlock("B", 1.0))
            self.addBlock(ProductBlock("amp"))
            self.addBlock(ProductBlock("per"))
            #   Using a buffer, the memory won't be flooded
            self.addBlock(SignalCollectorBlock("plot", buffer_size=500))

            # Create the Connections
            self.addConnection("B", "per")
            self.addConnection("time", "per")
            self.addConnection("per", "sin")
            self.addConnection("A", "amp")
            self.addConnection("sin", "amp")
            self.addConnection("amp", "plot")

The Dashboard
-------------
As per :doc:`LivePlot`, a TkInter window is being created and a :class:`CBD.realtime.plotting.PlotManager`
is assigned to display the plot. Notice there is an additional callback to ensure the y-axis will remain
in the range of :code:`[-1.0, 1.0]` if the values are smaller, but the axis may grow to a larger scope if
needs be.

.. code-block:: python

    from CBD.realtime.plotting import PlotManager, LinePlot, follow
    import matplotlib.pyplot as plt
    import tkinter as tk
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    fig = plt.figure(figsize=(15, 5), dpi=100)
    ax = fig.add_subplot(111)
    ax.set_ylim((-1, 1))

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

Next, let's provide a way of obtaining user information. We will use two TkInter :code:`Scale` objects to provide easy
input fields for the variables :code:`A` (the amplitude) and :code:`B` (proportional to the period). Additionally, a
:code:`Label` will show the current equation that is being plotted as additional information. The :func:`set_amplitude`
and :func:`set_period` functions make use of the ability of setting a :class:`CBD.lib.std.ConstantBlock`'s value
during runtime. Take a look at the corresponding documentations for more information.

.. danger::
    Do not alter the window closing protocol of the :code:`tkinter` root! It is automatically altered to ensure all
    threads are closed.

.. code-block:: python

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

And that's it! All that is left to do is to run the simulation and see how the plot interacts to user input.
Notice how no time constraint is set on the simulation. This will ensure there can be plenty of experimentation
by the user. Also, the :class:`CBD.lib.endpoints.SignalCollectorBlock` that is used was given a buffer size of
500 datapoints. This prevents the memory being flooded with data while this simulation is running (for an infinite
time).

.. code-block:: python

    from CBD.simulator import Simulator

    sim = Simulator(cbd)
    sim.setRealTime()
    sim.setRealTimePlatformTk(root)
    sim.setDeltaT(0.1)
    sim.run()
    root.mainloop()

While changing the values (especially the period), a lot of noice will appear. This is caused by the fact that
every update to a slider alters a result from another function that may be at a completely different location.
Lower the resolution for the scales to minimize this effect.

.. figure:: ../_figures/sin-dashboard.png
