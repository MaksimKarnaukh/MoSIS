Using CBDs with LEGO MINDSTORMS EV3
===================================

The LEGO MINDSTORMS EV3 can be fully accessed via Python-code.
Combined with the usefulness of CBDs for continuous embedded
systems, it stands to reason the CBD simulator can be used to
access the EV3 system. To do so, :code:`pybricks`
(:code:`micropython`) will be used.

In order to do so, follow `these installation instructions from
the pybricks website
<https://pybricks.com/ev3-micropython/startinstall.html>`_.
This creates a (bootable) flashed microSD card that can run Python
code. Simply write your CBD models and start your simulation!

For convenience, some building blocks are prebuild in this
:code:`CBD.lib.ev3` module.

.. automodule:: CBD.lib.ev3
    :members:
    :undoc-members:
    :show-inheritance:
