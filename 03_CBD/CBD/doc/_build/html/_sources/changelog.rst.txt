Changelog
=========

.. code-block:: text

    Version 1.6
        + Added communication interval to the core to be taken into account
          by tracers.
        + Added CSV, MAT and VCD Tracers
        * Changed project name from CBD to pyCBD

    Version 1.5
        * Changed how ports work. Instead of using PortBlocks, a custom Port
          (and Connection) class has been introduced.
            - InputPortBlock, WireBlock and OutputPortBlock were removed.
            * Flattening now ignores empty CBD blocks and in-between ports.
        * Some functions have been renamed to have a more descriptive name.
            * linkInput was changed to linkToInput
            * getSignals was split to getOutputPortNames and getSignalHistory
        * naivelog now uses the standard Python logging module.
        * Changed realtime simulation to be used more efficiently.
            * Pubsub structure now runs asynchronously.
            * Tracing now happens asynchronously.
        - Removed the CBD2C module to reduce code duplication w.r.t. the
          CBD2FMU project.
        + Plotting framework now works with Bokeh.

    Version 1.4
        + Added DeltaTBlock
        - Removed "delta_t" input port of IntegratorBlock and DerivatorBlock
        + Added SympySolver
        * Bugfixes:
             #21: KeyError CBD <...> in LinearSolver.constructInput
             #22: AssertionError because a DelayBlock is part of an algebraic
                  loop at iteration 1.
             #25: Tests make use of Clock
             #30: None vs int comparison failed

    Version 1.3
        *   Optimized LaTeX renderer. Now, it can also output a stepwise
            trace of the system.
        *   Renamed CBD.py -> Core.py to prevent "from CBD.CBD import CBD"
        +   Added simple equation to CBD converter: eq2CBD.
        *   Extracted simulation clock to custom block.
        -   Removed "old" Variable Step Size simulation system.
        +   Added Runge-Kutta preprocessor with generic Butcher Tableau.
        *   Made tests succeed once again.

    Version 1.2
        +   Added "multi-rate" simulation.
        *   Extracted topological sort to Schedule system.
        +   Added Variable Step Size simulation.
        *   Increased documentation coverage.

    Version 1.1
        +   Created Dashboard Example
        +   Added live plotting
        +   Added "endpoints" and "io" modules

    Version 1.0
        *   Reworked old "single-file" version to better structure.
        +   Added realtime simulation (in the PyPDEVS backends).
        +   Added progress bars.
        *   Made algebraic loop solver flexible and more efficient.
        +   Added docs.
