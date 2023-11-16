How to install the pyCBD framework?
===================================
This section describes the necessary components and steps to take to install
the CBD framework.

Dependencies
------------
The following dependencies are required:

* Python :code:`>= 3.6`, as identified by `vermin <https://pypi.org/project/vermin/>`_.
* All additional libraries should be bundled with Python, so no extra installations should be needed.

.. versionchanged:: 1.5
    Python 2 is no longer supported.

Next, there are some additional **optional** requirements:

* **Simulation:**

  * `tqdm <https://tqdm.github.io/>`_ when using a progress-bar of the simulation.
  * `TkInter <https://docs.python.org/3/library/tkinter.html>`_ for realtime simulation using the
    :code:`Tk` backend/platform.

* **Visualization and Plotting:**

  * `GraphViz <https://www.graphviz.org/download/>`_ for generating a graphical version of the dependency graph.
  * `MatPlotLib <https://matplotlib.org/>`_ for plotting data in Matplotlib.
  * `Seaborn <https://seaborn.pydata.org/>`_ for plotting data using Seaborn.
  * `Bokeh <https://docs.bokeh.org/en/latest/index.html>`_ for plotting data in Bokeh.

* **Conversion:**

  * `Lark <https://lark-parser.readthedocs.io/en/latest/>`_ for the :mod:`pyCBD.converters.eq2CBD` converter, to
    allow the creation of CBDs directly from a textual language.
  * `PythonPDEVS <http://msdl.cs.mcgill.ca/projects/DEVS/PythonPDEVS>`_ for the :mod:`pyCBD.converters.hybrid`
    module. This allows CBDs to be run inside of DEVS simulations.

* **Documentation:**

  * `Sphinx-Theme <https://pypi.org/project/sphinx-theme/>`_ for creating the docs.

Installation
------------
There are a few ways of using the framework:

#. Use it as a project dependency. Simply add the :code:`src/pyCBD` folder to your project and
   import it w.r.t. the provided path.
#. Edit the :code:`PYTHONPATH` or :code:`sys.path` variables to point to the :code:`src` folder.
   This way, the execution of your program will recognize things like:

   .. code-block:: python

      from pyCBD.Core import CBD

   .. tip::
        Some code editors (like `PyCharm <https://www.jetbrains.com/pycharm/>`_) allow you to mark
        a directory as "Sources Root", which basically adds it to your path upon execution.

#. Execute one of the following commands in the :code:`src` folder to install the project to your
   user directory or update it:

   .. code-block:: bash

      # BUILDING:
      python setup.py install --user

      # UPDATING:
      python -m pip install .

Standalone
----------
There are some additional standalone components that have been made to work with
the framework, but can technically be used without the connection to CBDs. These are:

.. toctree::
    :maxdepth: 3

    pyCBD.util
    pyCBD.naivelog
    pyCBD.realtime
