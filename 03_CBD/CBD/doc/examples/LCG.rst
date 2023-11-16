Linear Congruential Generator
=============================
A linear congruential generator (LCG) is a random number generator (RNG)
that follows the equation:

.. math::

    x(i) = (a\cdot x(i-1) + c) \mod m

Because of this, we can represent it as a CBD model. If you're not sure
how to create such a model, please take a look at the :doc:`SinGen`,
:doc:`EvenNumberGen` and :doc:`Fibonacci` examples.

.. code-block:: python

    from CBD.Core import CBD
    from CBD.lib.std import *

    class LCG(CBD):
        def __init__(self, block_name, a, c, m, x0):
            CBD.__init__(self, block_name, input_ports=[], output_ports=["OUT1"])

            # Create the Blocks
            self.addBlock(ConstantBlock("a", value=a))
            self.addBlock(ConstantBlock("x0", value=x0))
            self.addBlock(ConstantBlock("c", value=c))
            self.addBlock(ConstantBlock("m", value=m))
            self.addBlock(DelayBlock("delay"))
            self.addBlock(ProductBlock("mult"))
            self.addBlock(AdderBlock("sum"))
            self.addBlock(ModuloBlock("mod"))

            # Create the Connections
            self.addConnection("x0", "delay", input_port_name='IC')
            self.addConnection("a", "mult")
            self.addConnection("delay", "mult")
            self.addConnection("mult", "sum")
            self.addConnection("c", "sum")
            self.addConnection("sum", "mod", input_port_name='IN1')
            self.addConnection("m", "mod", input_port_name='IN2')
            self.addConnection("mod", "delay", input_port_name='IN1')
            self.addConnection("delay", "OUT1")

Termination Condition
---------------------
Instead of terminating our simulation after a certain time-period, we will
set a termination time whenever we see a number we've already seen. This
gives the following termination function:

.. code-block:: python

    def term(model, curIt):
        signals = [y for _, y in model.getSignalHistory("IN1")]
        unique_signals = set(signals)
        return len(signals) > len(unique_signals)

As you can see, this function returns :code:`True` whenever there are more
values than unique values. Whenever this happens, we must have encountered a
duplicate value.

Now, we can set up and run the simulation:

.. code-block:: python

    from CBD.simulator import Simulator

    lcg = LCG("LCG", 1, 4, 9, 0)
    sim = Simulator(lcg)
    sim.setTerminationCondition(term)
    sim.run()

    # Print a full cycle: [0, 4, 8, 3, 7, 2, 6, 1, 5]
    print([v for _, v in lcg.getSignalHistory("IN1")])
