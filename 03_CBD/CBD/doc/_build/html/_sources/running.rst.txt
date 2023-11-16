How to run a CBD simulation?
============================

A simple, local distribution can be executed by running an experiment file,
which will look like this:

.. code-block:: python

    model = MyModel()
    sim = Simulator()
    sim.run()

For a more elaborate setup, you can take add some configuration information to
the simulator (before the :func:`run` method is called); for instance:

.. code-block:: python

    # Set the step delay to 0.1 seconds
    sim.setDeltaT(0.1)

    # Set the termination time to 500 seconds
    sim.setTerminationTime(500)

    # Set the the system to terminate whenever cond(model) returns True
    # Take a look at the LCG example for more information
    sim.setTerminationCondition(cond)

    # Show a progress indicator (requires `tqdm` to be installed)
    sim.setProgressBar()

Take a look at the :class:`pyCBD.simulator.Simulator` class for more options
and information.

Running the Tests
-----------------
Not sure your code base is valid anymore? The CBD framework comes with its
own battery of tests (located in the :code:`src/test` folder), which can
be executed from the root folder with:

.. code-block:: bash

    python -m unittest discover -v src.test "*.py"
