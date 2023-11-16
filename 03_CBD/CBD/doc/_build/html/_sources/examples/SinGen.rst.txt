Sine Generator
==============

A very simple example usage of the framework is to create a CBD model
that implements the equation :math:`y = sin(t)`, where :math:`t` is
the simulation time and :math:`y` an output signal we're interested in.

Luckily, the standard library provides some functionalities to help us
solve this problem. Let's import three blocks:

.. code-block:: python

    from CBD.Core import *   # To prevent circular dependency
    from CBD.lib.std import TimeBlock, GenericBlock

The :class:`CBD.lib.std.TimeBlock` will output the current simulation time
every delta timeunits. This block will be used to obtain the :math:`t`
variable. The :class:`CBD.lib.std.GenericBlock` is a generic interface to
Python's :mod:`math` module. We will use this block to implement the sine
function itself.

Next, we need a container to group these blocks in. This is done in the
hierarchical :class:`CBD.Core.CBD` class. Let's call this "grouping" block
:code:`SinGen` and give it a single output port, named :code:`OUT1`.

.. code-block:: python

    class SinGen(CBD):
        def __init__(self, name="SinGen"):
            CBD.__init__(self, name, input_ports=[], output_ports=["OUT1"])

            # Add the 't' parameter
            # Let's call it 'time'
            self.addBlock(TimeBlock("time"))

            # Add the block that computes the actual sine function
            # Let's call it 'sin'
            self.addBlock(GenericBlock("sin", block_operator="sin"))

            # Connect them together
            self.addConnection("time", "sin", output_port_name='OUT1',
                                                input_port_name='IN1')

            # Connect the output port
            self.addConnection("sin", "OUT1", output_port_name='OUT1')


    sinGen = SinGen("SinGen")

Notice how this is semantically equivelent to:

.. code-block:: python

    from CBD.Core import CBD

    sinGen = CBD("SinGen", [], ["OUT1"])

    # Add the time, just like above
    sinGen.addBlock(TimeBlock("time"))

    sinGen.addBlock(GenericBlock("sin", block_operator="sin"))
    sinGen.addConnection("time", "sin", output_port_name='OUT1',
                                        input_port_name='IN1')
    sinGen.addConnection("sin", "OUT1", output_port_name='OUT1')

If we now want to simulate our model for 20 seconds (of simulation-time), we can
simply do:

.. code-block:: python

    from CBD.simulator import Simulator

    sim = Simulator(sinGen)
    # The termination time can be set as argument to the run call
    sim.run(20.0)

Next, we would like to obtain the accumulated simulation data on the :code:`OUT1`
output port of the :code:`sinGen` block, which can be plotted against their iteration
(which is equivalent to the time in this case).

.. code-block:: python

    data = sinGen.getSignalHistory('OUT1')
    x, y = [x for x, _ in data], [y for _, y in data]

.. figure:: ../_figures/sin-disc.png

Now, this is obviously not the sine wave we know and love. This is because our simulator
only computes at 0, 1, 2, 3... seconds, but not in-between. This can be changed by altering
the time delta **before** the start of a simulation:

.. code-block:: python

    sim.setDeltaT(0.1)

Now, we interpolate the sine-wave every 10th of a second, which looks much better:

.. figure:: ../_figures/sin-cont.png

.. seealso::

   :mod:`CBD.lib.std`: The standard set of CBD building blocks that can be used.

