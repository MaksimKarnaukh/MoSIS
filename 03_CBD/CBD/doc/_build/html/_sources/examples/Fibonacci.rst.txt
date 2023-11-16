Fibonacci Sequence Generator
============================

This section describes the usage of the more complex :class:`CBD.lib.std.DelayBlock`.
It will always output the previous value whenever it receives a new one, unless (obviously),
there is no previous value (e.g. at the beginning of the simulation). In that case, its
output is the value it obtains from the :code:`IC`.

We will create a generator that outputs the Fibonacci numbers, starting from :code:`1`,
:code:`1`, :code:`2`, :code:`3`, :code:`5`...; or more mathematically:

.. math::

    y(i) &= y(i - 1) + y(i - 2)\\
    y(0) &= y(1) = 1

For this we need the :class:`CBD.lib.std.AdderBlock` and obviously the
:class:`CBD.lib.std.DelayBlock`. Additionally, the :class:`CBD.lib.std.ConstantBlock`
will need to be used, as will be discussed later on.

.. code-block:: python

    from CBD.Core import CBD
    from CBD.lib.std import ConstantBlock, AdderBlock, DelayBlock

By linking two delay blocks after one another and sending both outputs through the adder,
we can implement the first equation. This yields:

.. code-block:: python

    class FibonacciGen(CBD):
        def __init__(self, block_name):
            CBD.__init__(self, block_name, input_ports=[], output_ports=['OUT1'])

            # Create the Blocks
            self.addBlock(DelayBlock("delay1"))
            self.addBlock(DelayBlock("delay2"))
            self.addBlock(AdderBlock("sum"))

            # Create the Connections
            self.addConnection("delay1", "delay2")
            self.addConnection("delay1", "sum")
            self.addConnection("delay2", "sum")
            self.addConnection("sum", "delay1", input_port_name='IN1')
            self.addConnection("sum", "OUT1")

Now, at time :code:`0` **and** at time :code:`1`, we would like to output :code:`1`.
We know:

.. math::

    y(0) &= delay1.IC + delay2.IC &= 1 \\
    y(1) &= delay1(1) + delay2(1) &= y(0) + delay1.IC\\
    & \Leftrightarrow \\
    delay1.IC &= 0\\
    delay2.IC &= 1

Do, let's add this to our model:

.. code-block:: python

        self.addBlock(ConstantBlock("zero", value=0))
        self.addBlock(ConstantBlock("one", value=1))

        self.addConnection("zero", "delay1", input_port_name='IC')
        self.addConnection("one", "delay2", input_port_name='IC')

The complete generator is therefore as follows:

.. code-block:: python

    from CBD.Core import CBD
    from CBD.lib.std import ConstantBlock, AdderBlock, DelayBlock

    class FibonacciGen(CBD):
        def __init__(self, block_name):
            CBD.__init__(self, block_name, input_ports=[], output_ports=['OUT1'])

            # Create the Blocks
            self.addBlock(DelayBlock("delay1"))
            self.addBlock(DelayBlock("delay2"))
            self.addBlock(AdderBlock("sum"))
            self.addBlock(ConstantBlock("zero", value=0))
            self.addBlock(ConstantBlock("one", value=1))

            # Create the Connections
            self.addConnection("delay1", "delay2")
            self.addConnection("delay1", "sum")
            self.addConnection("delay2", "sum")
            self.addConnection("sum", "delay1", input_port_name='IN1')
            self.addConnection("sum", "OUT1")
            self.addConnection("zero", "delay1", input_port_name='IC')
            self.addConnection("one", "delay2", input_port_name='IC')

When running the simulation for 10 time-units, we obtain the first 10 values:

.. code-block:: python

    from CBD.simulator import Simulator

    cbd = FibonacciGen("FibonacciGen")
    sim = Simulator(cbd)
    sim.run(10)
    data = cbd.getSignalHistory('OUT1')
    t, v = [t for t, _ in data], [v for _, v in data]

    print(v)  # prints [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]

.. image:: ../_figures/fib.png
    :width: 600
