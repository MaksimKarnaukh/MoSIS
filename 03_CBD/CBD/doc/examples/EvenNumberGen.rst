Hierarchical Even Number Generator
==================================
Assuming you have seen the basics from the :doc:`SinGen`, this
section will describe a simplistic even number generator, using
hierarchical CBD modelling.

At every timestep in the model, the generator is required to
output its double. We can split it up into two components: a
:class:`CBD.lib.std.TimeBlock` and a :code:`Double` CBD class,
which computes the double of its input. The generator block
can be constructed just like the :code:`SinGen` block was created
in the :doc:`SinGen` example:

.. code-block:: python

    from CBD.Core import CBD
    from CBD.lib.std import TimeBlock

    class EvenNumberGen(CBD):
        def __init__(self, name="EvenNumberGen"):
            CBD.__init__(self, name, input_ports=[], output_ports=["OUT1"])

            self.addBlock(TimeBlock("time"))
            self.addBlock(Double("double"))

            self.addConnection("time", "double", output_port_name='OUT1',
                                                 input_port_name='IN1')
            self.addConnection("double", "OUT1", output_port_name='OUT1')


    numGen = EvenNumberGen("NumGen")

Now, we're left with the construction of the :code:`Double` block, which basically
multiplies its input with 2:

.. code-block:: python

    from CBD.lib.std import ProductBlock, ConstantBlock

    class Double(CBD):
        def __init__(self, name="Double"):
            CBD.__init__(self, name, input_ports=["IN1"], output_ports=["OUT1"])

            # Create the blocks
            self.addBlock(ConstantBlock("two", 2))
            self.addBlock(ProductBlock("mult"))

            # Connect the blocks
            # Default ports are "INx" and "OUT1", with 'x' the index of the connection
            self.addConnection("two", "mult")
            self.addConnection("IN1", "mult")
            self.addConnection("mult", "OUT1")

And that's it. Now your models can have hierarchy!

Flattening
----------
Of course, when building highly hierarchical models, it may be useful to be able to
create a full model, ignoring all hierarchical model conceptions. Flattening is the
reverse of hierarchical composition. By calling the :func:`CBD.Core.CBD.flatten`
method, the CBD model will be transformed into a single CBD model without hierarchy.
