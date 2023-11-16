Continuous Time Simulation
==========================
Given that continuous time simulation will always have to be discretized when
executed, it is important to ask *how* this discretization happens. In the
:doc:`SinGen` example, this was done by reducing the delta inbetween multiple
steps. However, this may compute too often for what is required in a given
simulation. Assume we have the following data (from a sine wave):

.. figure:: ../_figures/stepsize/sine.png
   :width: 600

Fixed Step Size
---------------
With the previously discussed technique, the data could be plot using a fixed
step size, where the new data is being computed every :code:`dt` time. The
smaller this :code:`dt` value is, the more precise the plot. Below, the same
function has been plot twice, for :code:`dt = 0.5` and :code:`dt = 0.1`, where
the marked points on the plot highlight *when* the data has been recomputed. It
is clear from these plots that a smaller step size identifies more accurate
results.

.. figure:: ../_figures/stepsize/sine-5.png
   :width: 600

.. figure:: ../_figures/stepsize/sine-1.png
   :width: 600

This behaviour is the default in the simulator. This can be explicitly set as follows
(assuming :code:`sim` is the simulator object):

.. code-block:: python

   sim.setDeltaT(0.5)

This was done for academic reasons, as it is much easier to explain CBDs with a
fixed step size, as compared to varying step sizes. By default, the :code:`dt` is
set to 1.

Manipulating the Clock
----------------------
To maintain the block structure of the simulator, the simulation clock
(see :class:`CBD.lib.std.Clock`) is implemented as an actual block. If this clock is
not used in the model to simulate, the simulator will automatically add a fixed-rate
clock, given the :code:`dt` information, as explained above. This can also be done
manually via calling :func:`CBD.Core.CBD.addFixedRateClock`. The clock will actually
be used to compute the simulation time. The :class:`CBD.lib.std.TimeBlock` outputs the
current simulation time and can therefore be used to access the current time without
the need for the actual clock. However, blocks that depend on the :code:`dt` value
either need to be linked to a Clock block, or should have an input that yields the
correct value; i.e., a :class:`CBD.lib.std.ConstantBlock`.

Adaptive Step Size
------------------
Adaptive step size (or variable step size) is a simulation method in which the delta
changes throughout the simulation time. The clock-as-a-block structure allows the
variation of the :code:`dt`, as is required for adaptive step size. This can be done
manually by computing some simulation outputs, or via RK-preprocessing.

.. note::
    Runge-Kutta preprocessing is only available if there are one or more instances of
    :class:`CBD.lib.std.IntegratorBlock` in the original model. Also make sure not to
    use a flattened model to prevent errors.

The :class:`CBD.preprocessing.rungekutta.RKPreprocessor` transforms the original CBD
model into a new block diagram that applies the Runge-Kutta algorithm with error
estimation. The full family of Runge-Kutta algorithms can be used as long as they are
representable in a Butcher tableau. Take a look at
:class:`CBD.preprocessing.butcher.ButcherTableau` to see which algorithms are automatically
included.

For instance, to apply the Runge-Kutta Fehlberg method for 4th and 5th order to ensure
adaptive step size of a CBD model called :code:`sinGen`, the following code can be used:

.. code-block:: python

   from CBD.preprocessing.butcher import ButcherTableau as BT
   from CBD.preprocessing.rungekutta import RKPreprocessor

   # Add a clock to the model, or RK will not work, 1e-4 is the starting delta
   sinGen.addFixedRateClock("clock", 1e-4)

   tableau = BT.RKF45()
   RKP = RKPreprocessor(tableau, atol=2e-5, hmin=0.1, safety=.84)
   newModel = RKP.preprocess(oldModel)

.. warning::
    Notice how the :code:`preprocess` method returns a new model that must be used in the simulation.
    Make sure to refer to this model when reading output traces or changing constants (see also
    :doc:`Dashboard`).

.. warning::
    To obtain a block from the original model, the path :code:`RK.RK-K_0.block_name` could be used. However,
    because of the way RK works, it is perfectly possible there are multiple copies in the transformed model.
    It is discouraged to use the internal blocks for signal information. Therefore, please only read data
    from the output ports and not from blocks in the model itself. This is an unfortunate side-effect
    of "transforming" the model to comply to adaptive step size simulation.
