Realtime Simulation
===================
Besides normal (as-fast-as-possible) simulation, it is also possible to simulate CBD models in realtime. Here, the
time (and therefore `delta t` as well) will be interpreted as seconds and the simulator will wait **non-blocking**
until the required time has passed. There are several supported backend that provide this functionality. These
backends are based on the backends provided by PyPDEVS_.

While there doesn't have to be feedback duing a simulation, the :func:`CBD.simulator.Simulator.setProgressBar`
function provides a `tqdm progress bar <https://tqdm.github.io/>`_. When running long simulations, this might
be a useful feature. Note that, when combined with a termination condition, the progress bar may yield inaccurate
values.

.. note::
    - When using progress bars, `tqdm <https://tqdm.github.io/>`_ must be installed.
    - In :doc:`LivePlot`, realtime simulation is used together with a variation of the :doc:`SinGen` example.

.. note::
    Unlike PyPDEVS_, interrupt events are not possible. However, as can be seen in the :doc:`Dashboard`
    example, the :class:`CBD.lib.std.ConstantBlock` allows for altering the internal value it outputs
    **during** the simulation. This mechanism may be manipulated to allow for external interrupts if
    necessary.

.. _PyPDEVS: https://msdl.uantwerpen.be/documentation/PythonPDEVS/realtime.html

Example Model
-------------
To simplify the explanations of the following sections, we will be using the :doc:`SinGen` as a basis model.
To recap:

.. code-block:: python

    from CBD.Core import CBD
    from CBD.simulator import Simulator
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
    sim = Simulator(sinGen)
    sim.setRealTime()

.. note::
    Realtime simulation happens non-blocking. This means the :func:`CBD.simulator.Simulator.run` method will be called
    asynchronously. Additionally, simulation runs as a daemon thread, so exiting the main thread will automatically
    terminate the simulation. To keep the script alive until after the simulation, you can use:

    .. code-block:: python

        while sim.is_running():
            pass

    |

Python Threading Backend
------------------------
The threading (or Python) backend/platform will use the :mod:`threading` module for delaying the simulation steps.
This is the default simulation backend.

.. warning::
    Python threads can sometimes have a rather low granularity in CPython 2. So while we are simulating in soft
    realtime anyway, it is important to note that delays could potentially become significant.

.. code-block:: python

    sim.setRealTimePlatformThreading()
    sim.setDeltaT(0.3)
    sim.run(100.0)

    # Keep it alive
    while sim.is_running(): pass

    print("FINISHED!")

.. seealso::
    - :func:`CBD.simulator.Simulator.setRealTimePlatform`
    - :func:`CBD.simulator.Simulator.setRealTimePlatformThreading`
    - :func:`CBD.simulator.Simulator.is_running`

TkInter Backend
---------------
The `TkInter <https://docs.python.org/3/library/tkinter.html>`_ event loop can become quite complex, as it is
required to interface to the GUI as wel as to the simulation. Luckily, this backend will wrap all the complexity
into a white box. It is, however, required to define the GUI application and start the mainloop, but afterwards,
all will be handled for you.

.. code-block:: python

    import tkinter as tk

    root = tk.Tk()
    sim.setRealTimePlatformTk(root)
    sim.setDeltaT(0.3)
    sim.run(100.0)
    root.mainloop()

    print("FINISHED!")

.. seealso::
    - :func:`CBD.simulator.Simulator.setRealTimePlatform`
    - :func:`CBD.simulator.Simulator.setRealTimePlatformTk`

GameLoop Backend
----------------
Whenever it is required to control the invocation of delays from another execution loop, like e.g. a gameloop,
it is pertinent to make use of the `GameLoop` backend. Delays won't happen internally anymore, as they should be
handled by the execution loop. By making use of the :func:`CBD.simulator.Simulator.realtime_gameloop_call`, the
simulation can advance to the next timestep.

.. code-block:: python

    sim.setRealTimePlatformGameLoop()
    sim.setDeltaT(0.3)
    sim.run(100.0)

    while sim.is_running():
        # do some fancy computations
        ...

        # do some rendering
        ...

        # advance the model's state
        sim.realtime_gameloop_call()

    print("FINISHED!")

.. warning::
    The simulation is still variable on the time constraints of your current system. Use the
    :class:`CBD.realtime.threadingGameLoopAlt.ThreadingGameLoopAlt` instead to fully control the time yourself.
    In this case, the :func:`CBD.simulator.Simulator.realtime_gameloop_call` requires the simulation time to be
    passed as an argument.

    While this is an option, it is highly encouraged to use the other backends instead. The alternative gameloop
    runs on the bare bones of the simulator, making system invalidities possible when not fully understanding the
    simulator itself. Additionally, exploiting time in a simulation in this way is heavily discouraged and is
    considered to be a bad practice.

.. seealso::
    - :func:`CBD.simulator.Simulator.setRealTimePlatform`
    - :func:`CBD.simulator.Simulator.setRealTimePlatformGameLoop`
    - :func:`CBD.simulator.Simulator.realtime_gameloop_call`
    - :class:`CBD.realtime.threadingGameLoopAlt.ThreadingGameLoopAlt`
