Generate LaTeX from CBD Models
==============================

Bundled with the CBD simulator, there is a powerful CBD to equation converter.
It transforms an input CBD model into a set of equations, which can be outputted as
plaintext, or in LaTeX format.

.. note::
    For educational purposes, it is also possible to output all intermediary steps that
    were obtained in the generation of the final simplified equations.

As an example, the :doc:`examples/SinGen` will be used. It will be assumed the
:class:`SinGen` class exists and a CBD model is created for this class, stored in the
:code:`model` variable.
Additionally, it is important to import the :class:`pyCBD.converters.latexify.CBD2Latex` class:

.. code-block:: python

    # Create the model
    model = SinGen('model')

    # Import the latexify core unit
    from pyCBD.converters.latexify import CBD2Latex
    # OR, ALTERNATIVELY
    from pyCBD.converters.latexify.CBD2Latex import CBD2Latex

Next, we will create a converter, which can tell us the system of equations. For more information
about the keyword arguments of the class, take a look at the :class:`pyCBD.converters.latexify.CBD2Latex`
documentation.

.. code-block:: python

    cbd2latex = CBD2Latex(model, show_steps=True, render_latex=False)

To simplify the system of equations, you can call the
:func:`pyCBD.converters.latexify.CBD2Latex.CBD2Latex.simplify` method. When :code:`show_steps` was set to
:code:`True`, all steps and additional information will be outputted to the console. If :code:`show_steps`
was :code:`False`, you will see nothing in the console. After the simplification, you can obtain the
string-representation of the equations using the :func:`pyCBD.converters.latexify.CBD2Latex.CBD2Latex.render`
method.

.. code-block:: python

    cbd2latex.simplify()

    # print the resulting equations
    print("RESULT IS:")
    print(cbd2latex.render())

The output of this code is shown below:

.. code-block:: text

    INITIAL SYSTEM:
    sin.OUT1(i) = sin(sin.IN1(i))
    time.OUT1(i) = time(i)
    OUT1(i) = sin.OUT1(i)
    sin.IN1(i) = time.OUT1(i)

    STEP 1:  substituted all connections and constant values
    sin.OUT1(i) = sin(time(i))
    OUT1(i) = sin.OUT1(i)

    STEP 2:
    OUT1(i) = sin(time(i))

    RESULT IS:
    OUT1(i) = sin(time(i))



Submodules
----------

.. toctree::

   pyCBD.converters.latexify.CBD2Latex
   pyCBD.converters.latexify.functions
