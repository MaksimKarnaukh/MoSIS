Live Plotting of Data During the Simulation
===========================================
During a (realtime) simulation, often you would like to show some data that's being sent over a
certain connection. This can be intermediary data (i.e. the individual components of a computation),
system data (battery life, sensor information...) or output information (results, actuator inputs...).

Luckily, the CBD framework provides this functionality in a clean and efficient manner.

To allow for "live" plotting of data, make use of the :class:`CBD.realtime.plotting.PlotManager` class,
which is a wrapper for tracking multiple realtime plots. Internally, it will keep track of multiple
:class:`CBD.realtime.plotting.PlotHandler` instances to reduce code-overhead.

.. code-block:: python

    from CBD.realtime.plotting import PlotManager, ScatterPlot

    manager = PlotManager()

    # Register a scatter plot handler with name "myHandler", which listens to
    #   the data of the block "myBlock".
    manager.register("myHandler", MyBlock('myBlock'), figure, ScatterPlot())

Notice you also need a block that stores the data. For plotting a single signal, it's best to use the
:class:`CBD.lib.endpoints.SignalCollectorBlock`. Alternatively, to plot XY-pairs, the
:class:`CBD.lib.endpoints.PositionCollectorBlock` can be used.

Example Model
^^^^^^^^^^^^^
The examples below show how you can display a live plot for the :doc:`SinGen`, plotted in realtime.
The output of this block is removed and changed to a :code:`SignalCollectorBlock`:

.. code-block:: python

    from CBD.Core import CBD
    from CBD.lib.std import TimeBlock, GenericBlock
    from CBD.lib.endpoints import SignalCollectorBlock

    class SinGen(CBD):
        def __init__(self, name="SinGen"):
            CBD.__init__(self, name, input_ports=[], output_ports=[])

            # Create the blocks
            self.addBlock(TimeBlock("time"))
            self.addBlock(GenericBlock("sin", block_operator="sin"))
            self.addBlock(SignalCollectorBlock("collector"))

            # Connect the blocks
            self.addConnection("time", "sin")
            self.addConnection("sin", "collector")

    sinGen = SinGen("SinGen")

Using MatPlotLib
^^^^^^^^^^^^^^^^
The most common plotting framework for Python is `MatPlotLib <https://matplotlib.org/>`_. It provides
a lot of additional features and functionalities, but we will keep it simple. For more complexity, please
refer to their documentation.

.. note::
    While there are other plotting frameworks, `MatPlotLib` is by far the easiest to get live plotting
    to work.

Default
-------
If we're not concerned about a window manager in our system, we can easily make use of  `MatPlotLib`'s
builtin plotting window.

.. code-block:: python

    from CBD.realtime.plotting import PlotManager, LinePlot, follow, set_xlim
    from CBD.simulator import Simulator
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(5, 5), dpi=100)
    ax = fig.add_subplot(111)
    ax.set_ylim((-1, 1))    # The sine wave never exceeds this range
    plot = fig, ax

    manager = PlotManager()
    manager.register("sin", sinGen.find('collector')[0], plot, LinePlot(color='red'))
    manager.connect('sin', 'update', lambda d, axis=ax: axis.set_xlim(follow(d[0], 10.0, lower_bound=0.0)))
    # NOTE: alternatively, manager.set_xlim method can be used:
    #   manager.connect('sin', 'update', lambda d, p=plot: manager.set_xlim(p, follow(d[0], 10.0, lower_bound=0.0)))

    sim = Simulator(sinGen)
    sim.setRealTime()
    sim.setDeltaT(0.1)
    sim.run(20.0)

    plt.show()

.. figure:: ../_figures/sine-wave-mpl.gif
    :width: 400

Seaborn
-------
`Seaborn <https://seaborn.pydata.org/>`_ is a data visualization library, built on top of `MatPlotLib`.
Hence, it can be easily integrated and used for plotting live data. It can simply be used by providing
the :code:`PlotManager`'s constructor with a backend argument (the default argument is :code:`Backend.MPL`):

.. code-block:: python

    from CBD.realtime.plotting import Backend
    manager = PlotManager(Backend.SNS)  # OR: Backend.SEABORN

That's it. All other code remains the same. To change the theme to a `Seaborn` theme, you can either
`use a MatPlotLib theme <https://matplotlib.org/stable/gallery/style_sheets/style_sheets_reference.html>`_ theme,
or place the following code before the creation of the figure (see also
`Seaborn's documentation <https://seaborn.pydata.org/generated/seaborn.set_theme.html#seaborn.set_theme>`_ on
this topic):

.. code-block:: python

    import seaborn as sns
    sns.set_theme(style="darkgrid")  # or any of darkgrid, whitegrid, dark, white, ticks

.. _jupyter:

Jupyter Notebook
----------------
These days, `Jupyter Notebooks <https://jupyter.org/>`_ are the most common way to collect experiments.
Luckily, the :class:`CBD.realtime.plotting.PlotManager` can work with them without too much overhead. In fact,
all that's required is setting the magic function :code:`%matplotlib` **before** creating the plot. That's it!

A small caveat is the fact that a :code:`notebook` stays alive after the simulation finishes. This
means the :code:`PlotManager` keeps polling for data. To stop this, connect a signal that terminates this
polling to the simulator **before** starting the simulation:

.. code-block:: python

    # Kills all polling requests and closes the plots
    sim.connect("finished", manager.terminate)

    # Kills all polling requests, but keeps plots alive
    sim.connect("finished", manager.stop)

Also take a look at the :code:`examples/notebook` folder for more info.

TkInter
-------
Now, as mentioned in :doc:`RealTime`, there is also a :code:`TkInter` platform to run the realtime
simulation on. This can be useful for creating graphical user interfaces (GUIs). Sometimes, such a
GUI might be in need of a plot of the data. See also the :doc:`Dashboard` example for a more complex
variation.

.. code-block:: python

    from CBD.realtime.plotting import PlotManager, LinePlot, follow
    from CBD.simulator import Simulator

    import tkinter as tk
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    fig = plt.figure(figsize=(5, 5), dpi=100)
    ax = fig.add_subplot(111)
    ax.set_ylim((-1, 1))    # The sine wave never exceeds this range

    root = tk.Tk()

    # Create a canvas to draw the plot on
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

The plot will look exactly like the one for the default platform, except that it is inside a :code:`TkInter` window
now. Notice that we used the :code:`MatPlotLib` backend for visualization in :code:`TkInter`.

Using Bokeh
^^^^^^^^^^^
As an alternative for `MatPlotLib`, `Bokeh <https://docs.bokeh.org/en/latest/index.html>`_ kan be used. Bokeh creates
a server on which you can view your plots in the browser. To launch the server use the command below. When not using
this command, plots may start to "flicker" as the updates take too long.

.. code-block:: bash

    bokeh serve <experiment file>

.. note::
    In order to ensure that the :meth:`follow` function works for the x-axis, it is pertinent to set the
    :code:`x_range` attribute of the figure to the starting range. The same must be done for the y-axis.

    .. seealso::
        https://discourse.bokeh.org/t/how-to-update-x-range-y-range-in-callback/1586

.. note::
    For a clean termination of the plot, the :code:`PlotManager.stop` method needs to be called upon termination.
    Otherwise, Bokeh continues to actively poll for range updates, similar to :ref:`Jupyter Notebook <jupyter>`.

.. code-block:: python

    from CBD.realtime.plotting import PlotManager, Backend, LinePlot, follow
    from CBD.simulator import Simulator

    from bokeh.plotting import figure, curdoc

    sinGen = SinGen("sin")

    # IMPORTANT: x_range set, because this will be updated later!
    fig = figure(plot_width=500, plot_height=500, x_range=(0, 0), y_range=(-1, 1))
    document = curdoc()
    document.add_root(fig)

    # Use the Bokeh Backend
    manager = PlotManager(Backend.BOKEH)
    manager.register("sin", sinGen.find('collector')[0], fig, LinePlot(color='red'))
    manager.connect('sin', 'update', lambda d:
                        manager.bokeh_set_xlim(fig, document, follow(d[0], 10.0, lower_bound=0.0)))

    sim = Simulator(sinGen)
    sim.connect("finished", manager.stop)  #<< Stop polling the plots for updates
    sim.setRealTime()
    sim.setDeltaT(0.1)
    sim.run(20.0)


.. figure:: ../_figures/sine-wave-bokeh.gif
    :width: 400

.. warning::
    The simulation keeps running in the backend until the server is (requested to be) terminated. This is
    because `Bokeh` does not have accurate client closure hooks. Please contact the repo authors if you find
    a way to do this. Normally, users should not experience any issues because of this.

Configuration
^^^^^^^^^^^^^
The :mod:`CBD.realtime.plotting` module has a lot of configuration possibilities and options that allow
a wide range of visualisations. The examples above only differ in the plotting backend, but there exist
many more possibilities.

Following the Signal
--------------------
Notice how the above examples all have a line similar to:

.. code-block:: python

    manager.connect('sin', 'update', lambda d, a=ax: a.set_xlim(follow(d[0], 10.0, lower_bound=0.0)))

This line connects a callback function that must be executed each time the :code:`sin` handler updates. In the
case above, the callback function will update the x-axis limits by using the powerful
:meth:`CBD.realtime.plotting.follow` method. It will follow the most recent value by using a sliding window of
size 10. The signal will be kept in the center (default) and the window will not show values lower than 0.

It's this function that allows the nice looking plot following. Take a look at the documentation for
a detailed explanation on how this function can be used for more complex scenarios.

.. note::
    If you want to change both axes, either group the axis update in a helper function, or connect multiple
    callback functions.

Different Kinds of Plots
------------------------
Besides the default line plot, there are some additional kinds provided. Each of these plot kinds allow
configuration using the backend (keyword) arguments. These are passed to the manager during registration
(notice the :code:`LinePlot` class in the code above). Simply changing this class can produce different
results.

.. glossary::

    Line Plot (:class:`CBD.realtime.plotting.LinePlot`)
        The most common line plot was used in the above examples. It draws a straight line between all
        sequential points in the given dataset.

    Step Plot (:class:`CBD.realtime.plotting.StepPlot`)
        A line plot that applies zero-order hold mechanics. Instead of drawing a straight line to the next
        data point, it will stay horizontal and will "jump" up stepwise.

        .. figure:: ../_figures/sine-wave-step.gif
            :width: 400

    Scatter Plot (:class:`CBD.realtime.plotting.ScatterPlot`)
        Only draws the data points, does not create a line between them.

        .. figure:: ../_figures/sine-wave-scatter.gif
            :width: 400

    Arrow (:class:`CBD.realtime.plotting.Arrow`)
        Draws an arrow vector from a given :code:`position`, with a certain :code:`size`. This uses the
        latest y value from the data as the (radian) angle amongst the unit circle (i.e., counter-clockwise
        = positive angle). The :code:`update` signal may also update the :code:`position` and the :code:`size`.

        .. figure:: ../_figures/arrow-wave.gif
            :width: 400

