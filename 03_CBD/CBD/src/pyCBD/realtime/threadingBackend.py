# Copyright 2014 Modelling, Simulation and Design Lab (MSDL) at 
# McGill University and the University of Antwerp (http://msdl.cs.mcgill.ca/)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import threading


class Platform:
    """
    Identifies the platform to use in real-time simulation.
    """
    THREADING = "python"
    """
    Use the default Python threading platform.
    
    See Also:
        :class:`pyCBD.realtime.threadingPython.ThreadingPython`
    """

    PYTHON    = "python"
    """
    Use the default Python threading platform.
    
    See Also:
        :class:`pyCBD.realtime.threadingPython.ThreadingPython`
    """

    TKINTER   = "tkinter"
    """
    Use the TkInter backend, to allow GUIs of the simulation.
    
    See Also:
        :class:`pyCBD.realtime.threadingTkInter.ThreadingTkInter`
    """

    TK        = "tkinter"
    """
    Use the TkInter backend, to allow GUIs of the simulation.
    
    See Also:
        :class:`pyCBD.realtime.threadingTkInter.ThreadingTkInter`
    """

    GAMELOOP  = "loop"
    """
    Use a gameloop backend, to keep the time yourself.
    
    See Also:
        :class:`pyCBD.realtime.threadingGameLoop.ThreadingGameLoop`
    """

    LOOP      = "loop"
    """
    Use a gameloop backend, to keep the time yourself.
    
    See Also:
        :class:`pyCBD.realtime.threadingGameLoop.ThreadingGameLoop`
    """

    GLA      = "loop_alt"
    """
    Use an alternative gameloop backend, to keep the time yourself.
    
    See Also:
        :class:`pyCBD.realtime.threadingGameLoopAlt.ThreadingGameLoopAlt`
    """


class ThreadingBackend:
    """
    Wrapper around the actual threading backend.
    It will also handle interrupts and the passing of them to the calling thread.

    Args:
        subsystem (str):    String specifying the subsystem to use. Must be one of
                            :code:`python`, :code:`tkinter` or :code:`loop` (case-insensitive).
                            The :class:`Platform` class may be used to help identifying
                            the subsystem.
        args (list):        All additional arguments that should be passed to the subsystem's
                            constructor (must be a list). Only used for the :code:`tkinter`
                            subsystem.
    """
    def __init__(self, subsystem, args):
        self.interrupted_value = None
        if subsystem.lower() == Platform.THREADING:
            from .threadingPython import ThreadingPython
            self._subsystem = ThreadingPython()
        elif subsystem.lower() == Platform.TKINTER:
            from .threadingTkInter import ThreadingTkInter
            self._subsystem = ThreadingTkInter(*args)
        elif subsystem.lower() == Platform.GAMELOOP:
            from .threadingGameLoop import ThreadingGameLoop
            self._subsystem = ThreadingGameLoop()
        elif subsystem.lower() == Platform.GLA:
            from .threadingGameLoopAlt import ThreadingGameLoopAlt
            self._subsystem = ThreadingGameLoopAlt()
        else:
            raise Exception("Realtime subsystem not found: " + str(subsystem))

    def is_alive(self):
        """
        Checks that the main thread is alive.

        Returns:
            :code`True` when it is alive, otherwise :code:`False`.
        """
        return threading.main_thread().is_alive()

    def wait(self, time, func):
        """
        A non-blocking call, which will call the :code:`func` parameter after
        :code:`time` seconds. It will use the provided backend to do this.

        Args:
            time (float):       Time to wait in seconds.
            func (callable):    The function to call after the time has passed.
        """
        self._subsystem.wait(time, func)

    def step(self, time=0.0):
        """
        Perform a step in the backend; only supported for the game loop backend.

        Args:
            time (float):   The current simulation time. Only used if the alternative
                            gameloop backend is used.
        """
        if self._subsystem.__class__ == "ThreadingGameLoopAlt":
            self._subsystem.step(time)
        else:
            self._subsystem.step()

    def run_on_new_thread(self, func, args=()):
        """
        Runs a function on a new thread.
        Args:
            func (callable):    The function to execute.
            args (iter):        The arguments for the function.
        """
        p = threading.Thread(target=func, args=args)
        p.daemon = True
        p.start()
